"""Small, single-process email OTP MVP. Use shared persistent storage for production."""
import hashlib
import hmac
import os
import secrets
import smtplib
import string
import threading
import time
from collections import defaultdict, deque
from email.message import EmailMessage
from fastapi import Cookie, Depends, HTTPException

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O/1/I
TTL_SECONDS = 300
SESSION_SECONDS = 8 * 60 * 60
MAX_ATTEMPTS = 5
_lock = threading.RLock()
_challenges = {}  # email -> {digest, expires, attempts}
_sessions = {}  # token digest -> {email, expires}
_requests = defaultdict(deque)  # per email and IP

def allowed_accounts():
    return {
        email.strip().casefold(): role
        for key, role in (("ALLOWED_ADMIN_EMAIL", "admin"), ("ALLOWED_TEST_EMAIL", "tester"))
        if (email := os.getenv(key, "")).strip()
    }

def signing_key():
    value = os.getenv("AUTH_SECRET", "")
    if len(value) < 32:
        raise RuntimeError("AUTH_SECRET must be set to a random secret of at least 32 characters")
    return value.encode()

def digest(value):
    return hmac.new(signing_key(), value.encode(), hashlib.sha256).hexdigest()

def generate_code():
    return "".join(secrets.choice(ALPHABET) for _ in range(6))

def send_code(email, code):
    """SMTP: use Mailpit locally, authenticated TLS SMTP for real delivery."""
    host = os.getenv("SMTP_HOST", "localhost")
    port = int(os.getenv("SMTP_PORT", "1025"))
    sender = os.getenv("SMTP_FROM", "Smart Exam <login@example.invalid>")
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = email
    msg["Subject"] = "Smart Exam sign-in code"
    msg.set_content(f"Your sign-in code is: {code}\nIt expires in 5 minutes.\n")
    with smtplib.SMTP(host, port, timeout=10) as smtp:
        if os.getenv("SMTP_STARTTLS", "false").lower() == "true":
            smtp.starttls()
        username = os.getenv("SMTP_USERNAME")
        if username:
            smtp.login(username, os.environ["SMTP_PASSWORD"])
        smtp.send_message(msg)

def check_rate_limit(key, now, limit):
    records = _requests[key]
    while records and records[0] <= now - 3600:
        records.popleft()
    if len(records) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests; try again later")
    records.append(now)

def request_code(email, ip):
    normalized = email.strip().casefold()
    now = time.time()
    with _lock:
        check_rate_limit("ip:" + ip, now, 30)
        check_rate_limit("email:" + normalized, now, 10)
        if normalized not in allowed_accounts():
            return  # generic response, do not reveal whitelist
        code = generate_code()
        # Don't persist a challenge unless the email is accepted by SMTP.
        send_code(normalized, code)
        _challenges[normalized] = {
            "digest": digest(normalized + ":" + code),
            "expires": now + TTL_SECONDS,
            "attempts": 0,
        }

def verify_code(email, code, ip):
    normalized = email.strip().casefold()
    now = time.time()
    with _lock:
        check_rate_limit("verify-ip:" + ip, now, 60)
        challenge = _challenges.get(normalized)
        if not challenge or normalized not in allowed_accounts() or now >= challenge["expires"]:
            _challenges.pop(normalized, None)
            raise HTTPException(status_code=401, detail="Invalid or expired code")
        challenge["attempts"] += 1
        if challenge["attempts"] > MAX_ATTEMPTS:
            _challenges.pop(normalized, None)
            raise HTTPException(status_code=401, detail="Invalid or expired code")
        valid = hmac.compare_digest(challenge["digest"], digest(normalized + ":" + code.upper()))
        if not valid:
            if challenge["attempts"] >= MAX_ATTEMPTS:
                _challenges.pop(normalized, None)
            raise HTTPException(status_code=401, detail="Invalid or expired code")
        del _challenges[normalized]  # one-time use
        token = secrets.token_urlsafe(32)
        _sessions[digest(token)] = {"email": normalized, "expires": now + SESSION_SECONDS}
        return token

def get_current_user(smart_exam_session: str | None = Cookie(default=None)):
    if not smart_exam_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    with _lock:
        key = digest(smart_exam_session)
        entry = _sessions.get(key)
        if not entry or entry["expires"] <= time.time():
            _sessions.pop(key, None)
            raise HTTPException(status_code=401, detail="Session expired")
        role = allowed_accounts().get(entry["email"])
        if not role:
            raise HTTPException(status_code=403, detail="Account not allowed")
        return {"email": entry["email"], "role": role}

def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

def logout(token):
    if token:
        with _lock:
            _sessions.pop(digest(token), None)
