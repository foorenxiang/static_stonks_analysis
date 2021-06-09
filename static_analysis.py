import yaml
from pathlib import Path
from matplotlib import ticker
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime
from decimal import Decimal, ROUND_HALF_EVEN


def read_config(yaml_filepath):
    with open(yaml_filepath, "r") as fp:
        try:
            config = yaml.safe_load(fp)
        except yaml.YAMLError:
            print("Invalid configuration!")
    return config


def retrieve_ticker_data(tickerSymbol, period):
    tickerData = yf.Ticker(tickerSymbol)
    tickerDF = tickerData.history(period=period)
    return tickerDF


def round_value(measurement):
    roundedValue = Decimal(measurement).quantize(
        Decimal(".00"), rounding=ROUND_HALF_EVEN
    )
    return roundedValue


if __name__ == "__main__":
    """Read configuration"""
    config = read_config("config.yaml")
    ticker_symbols = config["stocks"]
    periods = config["period"]
    metrics = config["metrics"]

    for period in periods:
        """Save directory for figures"""
        save_folder = Path(f"{period}r")
        save_folder.mkdir(exist_ok=True)

        ticker_dfs = [
            {ticker: retrieve_ticker_data(ticker, period)} for ticker in ticker_symbols
        ]

        for dict_ in ticker_dfs:
            [(ticker, ticker_data)] = dict_.items()
            for metric in metrics:
                """Calculations"""
                date = datetime.date(datetime.now())
                ticker_series = ticker_data[metric]
                mean = ticker_series.mean()
                abs_std = ticker_series.std()

                """Plotting"""
                horizontal_plot_data = [
                    {
                        "label": "mean",
                        "value": mean,
                        "color": "#000000",
                    },
                    {
                        "label": "+1SD",
                        "value": mean + abs_std,
                        "color": "#0000DD",
                    },
                    {
                        "label": "+2SD",
                        "value": mean + (2 * abs_std),
                        "color": "#0000FF",
                    },
                    {
                        "label": "-1SD",
                        "value": mean - abs_std,
                        "color": "#DD0000",
                    },
                    {
                        "label": "-2SD",
                        "value": mean - (2 * abs_std),
                        "color": "#FF0000",
                    },
                    {
                        "label": "-5%",
                        "value": mean * 0.95,
                        "color": "#FF0000",
                    },
                    {
                        "label": "+5%",
                        "value": mean * 1.05,
                        "color": "#0000FF",
                    },
                ]

                plt.title(
                    f"{period}r {ticker} {metric} Mean Price: {round_value(mean)}USD {date}"
                )

                xmin, xmax = ticker_series.axes[0][0], ticker_series.axes[0][-1]
                for measurement in horizontal_plot_data:
                    plt.hlines(
                        y=measurement["value"],
                        xmin=xmin,
                        xmax=xmax,
                        colors=measurement["color"],
                        linestyles="-",
                        lw=2,
                        label=measurement["label"],
                    )
                    roundedValue = round_value(measurement["value"])
                    plt.text(
                        xmin,
                        roundedValue,
                        f"{measurement['label']}: {roundedValue}USD",
                    )

                ticker_series.plot()

                plt.savefig(save_folder / f"{ticker}_{metric}_{date}.jpg")
                plt.clf()
