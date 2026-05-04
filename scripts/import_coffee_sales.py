import sys
from pathlib import Path

import argparse

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from db_exercise.operations import DEFAULT_CSV, import_coffee_sales


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", type=Path, nargs="?", default=DEFAULT_CSV)
    args = parser.parse_args()

    print(import_coffee_sales(args.csv_file))


if __name__ == "__main__":
    main()
