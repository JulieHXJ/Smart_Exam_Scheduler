"""Desktop entry point: local API server + native window."""
import os
import secrets
import socket
import threading
import time
import urllib.request
from pathlib import Path

from dotenv import load_dotenv
from platformdirs import user_config_dir

APP_NAME = "SmartExam"
CONFIG_DIR = Path(user_config_dir(APP_NAME, appauthor=False))
CONFIG_FILE = CONFIG_DIR / "config.env"
CONFIG_TEMPLATE = """# SmartExam desktop settings. Replace the blank values before signing in.
ALLOWED_ADMIN_EMAIL=
ALLOWED_TEST_EMAIL=

# SMTP settings for sending sign-in codes
SMTP_HOST=
SMTP_PORT=587
SMTP_STARTTLS=true
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM=
"""


def configure_env() -> None:
    """Settings live in the user's profile, never inside the app folder."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists() or CONFIG_FILE.stat().st_size == 0:
        CONFIG_FILE.write_text(CONFIG_TEMPLATE, encoding="utf-8")
    if os.name == "posix":
        CONFIG_FILE.chmod(0o600)
    load_dotenv(CONFIG_FILE)
    # Sessions are in memory, so a fresh secret per launch costs nothing.
    os.environ.setdefault("AUTH_SECRET", secrets.token_urlsafe(48))
    os.environ.setdefault("AUTH_SECURE_COOKIE", "false")  # plain http on 127.0.0.1


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_until_up(port: int, timeout: float = 15) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1)
            return
        except OSError:
            time.sleep(0.2)
    raise RuntimeError("Backend did not start in time")


def main() -> None:
    configure_env()  # before importing the app, so env vars are in place

    import uvicorn
    import webview

    from app.main import app

    port = free_port()
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host="127.0.0.1",  # never expose the API to the network
            port=port,
            log_config=None,  # the default log setup crashes in a windowed .exe
            loop="asyncio",
            http="h11",
            ws="none",
        )
    )
    threading.Thread(target=server.run, daemon=True).start()
    wait_until_up(port)

    webview.create_window(
        "SmartExam", f"http://127.0.0.1:{port}", width=1440, height=900, min_size=(1100, 700)
    )
    webview.start()  # blocks until the window is closed
    server.should_exit = True


if __name__ == "__main__":
    main()