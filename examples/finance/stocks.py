import os
import warnings
import json
from tome.api.output import TomeOutput
from tome.command import tome_command
from tome.errors import TomeException
from rich.console import Console
from rich.table import Table
from rich import box

# Attempt to import non-standard libraries
try:
    from yahooquery import search, Ticker
except ImportError:
    search = None
    Ticker = None

warnings.filterwarnings("ignore", category=FutureWarning, module="yahooquery")


def get_stock_symbol(company_name):
    """
    Get the stock symbol from the company name.
    """
    if search is None:
        raise TomeException("yahooquery is not available.")
    search_result = search(company_name)
    if "quotes" in search_result and search_result["quotes"]:
        return search_result["quotes"][0]["symbol"]
    else:
        return None


def get_stock_data(stock_symbol):
    """
    Get the current value, currency, and performance data of the stock.
    """
    if Ticker is None:
        raise TomeException("yahooquery is not available.")
    stock = Ticker(stock_symbol)
    stock_info = stock.history(period="1d")
    if not stock_info.empty:
        current_value = float(stock_info["close"].iloc[-1])
        currency = stock.price[stock_symbol]["currency"]

        def get_percentage_change(period):
            history = stock.history(period=period)
            if not history.empty:
                return float(((history["close"].iloc[-1] - history["close"].iloc[0]) / history["close"].iloc[0]) * 100)
            return None

        # Get analyst ratings
        strong_buy = buy = hold = sell = strong_sell = 0
        recommendation_score = 0
        total_weight = 0

        # Use get_modules to get analyst data
        modules = stock.get_modules(
            [
                "recommendationTrend",
                "summaryDetail",
                "defaultKeyStatistics",
                "financialData",
            ]
        )

        if stock_symbol in modules:
            recommendation_trend = modules[stock_symbol].get("recommendationTrend", {})
            if "trend" in recommendation_trend:
                trends = recommendation_trend["trend"]
                # Apply weights to recent recommendations
                for index, trend in enumerate(trends):
                    weight = 1 / (index + 1)
                    strong_buy += trend.get("strongBuy", 0)
                    buy += trend.get("buy", 0)
                    hold += trend.get("hold", 0)
                    sell += trend.get("sell", 0)
                    strong_sell += trend.get("strongSell", 0)

                    total_recommendations = (
                        trend.get("strongBuy", 0)
                        + trend.get("buy", 0)
                        + trend.get("hold", 0)
                        + trend.get("sell", 0)
                        + trend.get("strongSell", 0)
                    )
                    if total_recommendations > 0:
                        recommendation_score += (
                            (
                                (trend.get("strongBuy", 0) * 1)
                                + (trend.get("buy", 0) * 0.5)
                                + (trend.get("hold", 0) * 0)
                                + (trend.get("sell", 0) * -0.5)
                                + (trend.get("strongSell", 0) * -1)
                            )
                            / total_recommendations
                            * weight
                        )
                        total_weight += weight

            summary_detail = modules[stock_symbol].get("summaryDetail", {})
            default_key_statistics = modules[stock_symbol].get("defaultKeyStatistics", {})
            financial_data = modules[stock_symbol].get("financialData", {})

            market_cap = summary_detail.get("marketCap")
            dividend_yield = summary_detail.get("dividendYield")
            week_high_52 = summary_detail.get("fiftyTwoWeekHigh")
            week_low_52 = summary_detail.get("fiftyTwoWeekLow")
            beta = summary_detail.get("beta")
            forward_pe = financial_data.get("forwardPE")

        if total_weight > 0:
            recommendation_score /= total_weight
        else:
            recommendation_score = None

        data = {
            "stock_symbol": stock_symbol,
            "current_value": current_value,
            "currency": currency,
            "change_1d": get_percentage_change("2d"),
            "change_1w": get_percentage_change("1wk"),
            "change_1m": get_percentage_change("1mo"),
            "change_6m": get_percentage_change("6mo"),
            "change_1y": get_percentage_change("1y"),
            "volume": int(stock_info["volume"].iloc[-1]),
            "pe_ratio": stock.price[stock_symbol].get("forwardPE"),
            "strong_buy": strong_buy,
            "buy": buy,
            "hold": hold,
            "sell": sell,
            "strong_sell": strong_sell,
            "market_cap": market_cap,
            "dividend_yield": dividend_yield,
            "52_week_high": week_high_52,
            "52_week_low": week_low_52,
            "beta": beta,
            "forward_pe": forward_pe,
            "recommendation_score": recommendation_score,
        }

        return data
    else:
        return None


def print_json_output(result):
    output = TomeOutput(stdout=True)
    output.print_json(json.dumps(result, indent=4))


def print_rich_table(data_list):
    console = Console()
    table = Table(title="Stock Data Comparison", box=box.SIMPLE_HEAVY)
    table.add_column("Stock Symbol", justify="right", style="cyan", no_wrap=True)
    table.add_column("Current Value", justify="right", style="green")
    table.add_column("Currency", justify="right", style="green")
    table.add_column("Change 1 Day (%)", justify="right", style="magenta")
    table.add_column("Change 1 Week (%)", justify="right", style="magenta")
    table.add_column("Change 1 Month (%)", justify="right", style="magenta")
    table.add_column("Change 6 Months (%)", justify="right", style="magenta")
    table.add_column("Change 1 Year (%)", justify="right", style="magenta")
    table.add_column("Volume", justify="right", style="yellow")
    table.add_column("P/E Ratio", justify="right", style="yellow")
    table.add_column("Market Cap", justify="right", style="green")
    table.add_column("Dividend Yield", justify="right", style="green")
    table.add_column("52 Week High", justify="right", style="green")
    table.add_column("52 Week Low", justify="right", style="green")
    table.add_column("Beta", justify="right", style="green")
    table.add_column("Forward P/E", justify="right", style="green")
    table.add_column("Recommendation Score", justify="right", style="green")

    for stock_data in data_list:

        def format_change(value):
            if value is None:
                return "N/A"
            return f"[green]{value:.2f}%[/green]" if value > 0 else f"[red]{value:.2f}%[/red]"

        table.add_row(
            stock_data["stock_symbol"],
            f"{stock_data['current_value']:.2f}",
            stock_data["currency"],
            format_change(stock_data["change_1d"]),
            format_change(stock_data["change_1w"]),
            format_change(stock_data["change_1m"]),
            format_change(stock_data["change_6m"]),
            format_change(stock_data["change_1y"]),
            f"{stock_data['volume']:,}",
            f"{stock_data['pe_ratio']:.2f}" if stock_data["pe_ratio"] is not None else "N/A",
            f"{stock_data['market_cap']:,}" if stock_data["market_cap"] is not None else "N/A",
            f"{stock_data['dividend_yield']:.2f}" if stock_data["dividend_yield"] is not None else "N/A",
            f"{stock_data['52_week_high']:.2f}" if stock_data["52_week_high"] is not None else "N/A",
            f"{stock_data['52_week_low']:.2f}" if stock_data["52_week_low"] is not None else "N/A",
            f"{stock_data['beta']:.2f}" if stock_data["beta"] is not None else "N/A",
            f"{stock_data['forward_pe']:.2f}" if stock_data["forward_pe"] is not None else "N/A",
            f"{stock_data['recommendation_score']:.2f}" if stock_data["recommendation_score"] is not None else "N/A",
        )

    console.print(table)


@tome_command(formatters={"text": print_rich_table, "json": print_json_output})
def stocks(tome_api, parser, *args):
    """
    Description of the command.
    """
    parser.add_argument(
        "queries",
        nargs="+",
        help="Stock symbols or 'query:<company_name>' to search for the stock symbols",
    )
    args = parser.parse_args(*args)

    tome_output = TomeOutput()
    results = []

    if search is None or Ticker is None:
        tome_output.error(
            "The required libraries for querying stock data are not available. Please install them by doing 'pip install yahooquery'"
        )
        return results

    for query in args.queries:
        if query.startswith("query:"):
            company_name = query.split("query:")[1]
            stock_symbol = get_stock_symbol(company_name)
            if not stock_symbol:
                tome_output.info(f"Could not find a stock symbol for the company: {company_name}")
                continue
        else:
            stock_symbol = query

        stock_data = get_stock_data(stock_symbol)
        if stock_data:
            results.append(stock_data)
        else:
            tome_output.info(f"No data available for stock symbol: {stock_symbol}")

    return results
