import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from db_exercise.operations import concurrency_demo


def main() -> None:
    print(concurrency_demo())


if __name__ == "__main__":
    main()
