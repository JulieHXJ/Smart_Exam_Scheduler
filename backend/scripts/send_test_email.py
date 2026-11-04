import sys

from dotenv import load_dotenv

load_dotenv()

from app.auth.core import generate_code, send_code  # noqa: E402


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m scripts.send_test_email <recipient>")
    recipient = sys.argv[1]
    try:
        send_code(recipient, generate_code())
    except Exception as exc:
        sys.exit(f"FAILED: {type(exc).__name__}: {exc}")
    print(f"Sent. Check the inbox (and spam folder) of {recipient}.")


if __name__ == "__main__":
    main()