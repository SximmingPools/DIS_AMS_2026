import argparse
import sys
from datetime import timedelta
from pathlib import Path

import psycopg
import matplotlib.pyplot as plt

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from db_exercise.config import database_url


def fetch_ingredient_series(target_ingredient: str) -> tuple[list, list[float], str]:
    with psycopg.connect(database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select distinct unit
                from daily_ingredient_usage
                where ingredient = %s
                order by unit
                """,
                (target_ingredient,),
            )
            units = [row[0] for row in cur.fetchall()]

            if not units:
                cur.execute(
                    """
                    select distinct ingredient
                    from daily_ingredient_usage
                    order by ingredient
                    """
                )
                available = [row[0] for row in cur.fetchall()]
                raise RuntimeError(
                    f"Ingredient not found: {target_ingredient}. "
                    f"Available ingredients: {', '.join(available)}"
                )

            if len(units) > 1:
                raise RuntimeError(
                    f"Ingredient {target_ingredient} has multiple units: {', '.join(units)}"
                )

            unit = units[0]

            cur.execute(
                """
                select sale_date, daily_usage
                from daily_ingredient_usage
                where ingredient = %s and unit = %s
                order by sale_date
                """,
                (target_ingredient, unit),
            )

            rows = cur.fetchall()

    dates = [row[0] for row in rows]
    values = [float(row[1]) for row in rows]

    return dates, values, unit


def moving_average_forecast(values: list[float], window: int, steps: int) -> list[float]:
    if window <= 0:
        raise ValueError("window must be positive")

    if steps <= 0:
        raise ValueError("steps must be positive")

    if len(values) < window:
        raise ValueError("not enough historical values for selected window")

    history = values[:]
    forecasts = []

    for _ in range(steps):
        prediction = sum(history[-window:]) / window
        forecasts.append(prediction)
        history.append(prediction)

    return forecasts


def evaluate_moving_average(values: list[float], window: int, test_size: int) -> tuple[list[float], float]:
    if test_size <= 0:
        raise ValueError("test_size must be positive")

    if len(values) <= window + test_size:
        raise ValueError("not enough values for selected window and test_size")

    train = values[:-test_size]
    actual = values[-test_size:]

    history = train[:]
    predictions = []

    for real_value in actual:
        prediction = sum(history[-window:]) / window
        predictions.append(prediction)
        history.append(real_value)

    absolute_errors = [
        abs(real - prediction)
        for real, prediction in zip(actual, predictions)
    ]

    mae = sum(absolute_errors) / len(absolute_errors)

    return predictions, mae

def create_plots(
    ingredient: str,
    unit: str,
    window: int,
    dates: list,
    values: list[float],
    future_dates: list,
    future_forecast: list[float],
    evaluation_dates: list,
    evaluation_actual: list[float],
    evaluation_forecast: list[float],
    mae: float,
) -> tuple[Path, Path]:
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    safe_ingredient = ingredient.lower().replace(" ", "_")

    future_plot = output_dir / f"future_forecast_{safe_ingredient}_window_{window}.png"
    evaluation_plot = output_dir / f"evaluation_forecast_{safe_ingredient}_window_{window}.png"

    plot_days = 60

    plt.figure(figsize=(12, 6))
    plt.plot(dates[-plot_days:], values[-plot_days:], label="Original data")
    plt.plot(future_dates, future_forecast, label="Future forecast", linestyle="--")
    plt.title(f"Future forecast: {ingredient}, Moving Average window={window}")
    plt.xlabel("Date")
    plt.ylabel(f"Daily usage ({unit})")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(future_plot)
    plt.close()

    plt.figure(figsize=(12, 6))
    plt.plot(dates[-plot_days:], values[-plot_days:], label="Original data")
    plt.plot(evaluation_dates, evaluation_forecast, label="Evaluation forecast", linestyle="--")
    plt.scatter(evaluation_dates, evaluation_actual, label="Evaluation actual")
    plt.title(f"Evaluation forecast: {ingredient}, window={window}, MAE={mae:.2f} {unit}")
    plt.xlabel("Date")
    plt.ylabel(f"Daily usage ({unit})")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(evaluation_plot)
    plt.close()

    return future_plot, evaluation_plot


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingredient", default="Milk")
    parser.add_argument("--window", type=int, default=7)
    parser.add_argument("--steps", type=int, default=14)
    parser.add_argument("--test-size", type=int, default=14)
    args = parser.parse_args()

    dates, values, unit = fetch_ingredient_series(args.ingredient)

    print("Input time series:")
    print(f"Observations available: {len(values)}")
    print(f"First date: {dates[0]}")
    print(f"Last date: {dates[-1]}")
    
    training_size = len(values) - args.test_size

    print(f"Training observations: {training_size}")
    print(f"Evaluation observations: {args.test_size}")
    print()

    future_forecast = moving_average_forecast(
        values=values,
        window=args.window,
        steps=args.steps,
    )

    evaluation_forecast, mae = evaluate_moving_average(
        values=values,
        window=args.window,
        test_size=args.test_size,
    )

    last_date = dates[-1]
    future_dates = [
        last_date + timedelta(days=index)
        for index in range(1, args.steps + 1)
    ]

    evaluation_dates = dates[-args.test_size:]
    evaluation_actual = values[-args.test_size:]

    future_plot, evaluation_plot = create_plots(
        ingredient=args.ingredient,
        unit=unit,
        window=args.window,
        dates=dates,
        values=values,
        future_dates=future_dates,
        future_forecast=future_forecast,
        evaluation_dates=evaluation_dates,
        evaluation_actual=evaluation_actual,
        evaluation_forecast=evaluation_forecast,
        mae=mae,
    )

    print("Algorithm: Moving Average")
    print(f"Ingredient: {args.ingredient}")
    print(f"Unit: {unit}")
    print(f"Window: {args.window}")
    print(f"Future forecast days: {args.steps}")
    print(f"Evaluation days: {args.test_size}")
    print(f"Evaluation MAE: {mae:.2f} {unit}")
    print()

    print("Future forecast:")
    print("date,forecast")
    for date, forecast in zip(future_dates, future_forecast):
        print(f"{date},{forecast:.2f}")

    print()
    print("Evaluation forecast:")
    print("date,actual,forecast,error")
    for date, actual, forecast in zip(evaluation_dates, evaluation_actual, evaluation_forecast):
        error = abs(actual - forecast)
        print(f"{date},{actual:.2f},{forecast:.2f},{error:.2f}")

    print()
    print(f"Future plot saved to: {future_plot}")
    print(f"Evaluation plot saved to: {evaluation_plot}")


if __name__ == "__main__":
    main()