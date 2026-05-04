import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from db_exercise.operations import check_connection


def main() -> None:
    print(check_connection())


if __name__ == "__main__":
    main()
