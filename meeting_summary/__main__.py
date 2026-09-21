"""Ermöglicht den Start mit ``python -m meeting_summary``."""

from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())
