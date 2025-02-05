import os
from tome.command import tome_command
from tome.api.output import TomeOutput
from tome.errors import TomeException


@tome_command()
def currency(tome_api, parser, *args):
    """
    Convert currency from one unit to another using current exchange rates.
    """
    parser.add_argument("amount", type=float, help="Amount to convert")
    parser.add_argument("from_currency", help="Currency to convert from (e.g., USD, EUR)")
    parser.add_argument("to_currency", help="Currency to convert to (e.g., USD, EUR)")
    parser.add_argument("-vp", "--vault-password", help="Tome vault password")
    parser.add_argument("--no-ssl", action="store_true", help="Disable SSL verification")
    args = parser.parse_args(*args)

    my_vault = tome_api.vault.open(password=args.vault_password)

    api_key = os.getenv("EXCHANGE_RATE_API_KEY") or my_vault.read(name="exchange-rate-api")
    if not api_key:
        raise TomeException(
            "API key for ExchangeRate-API not found in environment variables."
            "Please set the API Key in the 'EXCHANGE_RATE_API_KEY' environment variable or add it to."
            "the tome vault as 'exchange-rate-api'"
        )

    API_URL = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/"

    import requests

    tome_output = TomeOutput()

    try:
        response = requests.get(f"{API_URL}{args.from_currency.upper()}", verify=not args.no_ssl)
        data = response.json()

        if response.status_code != 200:
            tome_output.error(f"Error fetching exchange rates: {data.get('error-type', 'Unknown error')}")
            return

        rates = data.get("conversion_rates", {})
        if args.to_currency.upper() not in rates:
            tome_output.error(f"Unsupported target currency: {args.to_currency.upper()}")
            return

        rate = rates[args.to_currency.upper()]
        converted_amount = args.amount * rate
        tome_output.info(
            f"{args.amount} {args.from_currency.upper()} is equal to {converted_amount:.2f} {args.to_currency.upper()} at the current exchange rate."
        )
    except Exception as e:
        tome_output.error(f"An error occurred: {e}")
