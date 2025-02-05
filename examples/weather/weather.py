import os
from tome.command import tome_command
from tome.api.output import TomeOutput
from tome.errors import TomeException


def check_api_key():
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

    if not API_KEY:
        raise TomeException(
            "No API key found for OpenWeatherMap. Please set the OPENWEATHER_API_KEY environment variable."
        )


@tome_command()
def current(tome_api, parser, *args):
    """Get the current weather for a specific city."""
    parser.add_argument("city", help="The city to get the current weather for.")
    args = parser.parse_args(*args)

    check_api_key()

    import requests

    tome_output = TomeOutput()

    try:
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={args.city}&appid={API_KEY}&units=metric"
        )
        response.raise_for_status()
        data = response.json()
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        tome_output.info(f"Current weather in {args.city}: {weather_desc}, {temp}°C")
    except requests.exceptions.RequestException as e:
        tome_output.error(f"Error fetching weather data: {str(e)}")


@tome_command()
def forecast(tome_api, parser, *args):
    """Get the weather forecast for the next few days in a specific city."""
    parser.add_argument("city", help="The city to get the weather forecast for.")
    parser.add_argument(
        "--days",
        type=int,
        default=3,
        help="Number of days to get the forecast for (max 7).",
    )
    args = parser.parse_args(*args)

    import requests

    check_api_key()

    tome_output = TomeOutput()

    if args.days < 1 or args.days > 7:
        tome_output.error("Number of days must be between 1 and 7.")
        return

    try:
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/forecast/daily?q={args.city}&cnt={args.days}&appid={API_KEY}&units=metric"
        )
        response.raise_for_status()
        data = response.json()
        tome_output.info(f"Weather forecast for {args.city}:")
        for day in data["list"]:
            date = day["dt"]
            weather_desc = day["weather"][0]["description"]
            temp_day = day["temp"]["day"]
            temp_night = day["temp"]["night"]
            tome_output.info(f"{date}: {weather_desc}, Day: {temp_day}°C, Night: {temp_night}°C")
    except requests.exceptions.RequestException as e:
        tome_output.error(f"Error fetching weather data: {str(e)}")
