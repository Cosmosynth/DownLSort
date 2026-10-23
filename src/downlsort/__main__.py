"""Allow `python -m downlsort`."""

try:
    from .main import main
except ImportError:  # when frozen or running as script
    from downlsort.main import main

if __name__ == "__main__":
    main()
