import argparse
import logging
import sys
import time
from pathlib import Path

from sync import SyncManager

USAGE = f"Usage: python {sys.argv[0]} [--help] | source_path target_path sync_period log_path]"


def setup_logger(log_path):
    logging.basicConfig(filename=log_path, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(console)
    return logger


def parse_arguments():
    parser = argparse.ArgumentParser(description="Synchronize files from a SOURCE folder to a TARGET folder.")
    parser.add_argument("source_path", type=str, help="Path to the source folder")
    parser.add_argument("target_path", type=str, help="Path to the target folder")
    parser.add_argument("sync_period", type=int, help="Synchronization period in seconds")
    parser.add_argument("log_path", type=str, help="Path to the log file")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    source_path = Path(args.source_path)
    target_path = Path(args.target_path)
    sync_period = args.sync_period
    log_path = Path(args.log_path)

    if not all([source_path.exists(), target_path.exists(), log_path.exists()]):
        print("Ensure all paths exist in the system")
        sys.exit(1)

    logger = setup_logger(log_path)

    while True:
        sync_manager = SyncManager(source_path, target_path, logger)
        sync_manager.sync()
        print(f"Sleeping for {sync_period} seconds...")
        time.sleep(sync_period)


if __name__ == "__main__":
    main()
