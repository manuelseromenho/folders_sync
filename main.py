import sys

USAGE = f"Usage: python {sys.argv[0]} [--help] | source_path targe_path sync_period]"


def main () -> None:
    args = sys.argv[1:]
    if len(args) < 2:
        raise SystemExit(USAGE)

if __name__ == '__main__':
    main()
