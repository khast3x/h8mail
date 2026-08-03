import sys
from .utils.run import main

if __name__ == "__main__":
    if sys.version_info < (3, 10):
        sys.stdout.write(
            "\n/!\\ h8mail requires Python 3.10+ /!\\\n"
            "Check your interpreter with: python --version\n\n"
        )
        sys.exit(1)
    main()
