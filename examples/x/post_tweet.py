import os
from tome.command import tome_command
from tome.api.output import TomeOutput


@tome_command()
def tweet(tome_api, parser, *args):
    """
    Post a tweet on X (formerly Twitter).
    """
    parser.add_argument("message", help="The message to tweet")
    parser.add_argument("--image", help="Path to an image to attach to the tweet")
    args = parser.parse_args(*args)

    import tweepy

    # Twitter API credentials (replace with your actual credentials)
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret_key = os.getenv("TWITTER_API_SECRET_KEY")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    if not all([api_key, api_secret_key, access_token, access_token_secret]):
        tome_output = TomeOutput()
        tome_output.error("Twitter API credentials are not set in environment variables.")
        return

    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(api_key, api_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # Post the tweet
    try:
        if args.image:
            api.update_with_media(args.image, status=args.message)
            tome_output.info(f"Tweet posted with image: {args.image}")
        else:
            api.update_status(status=args.message)
            tome_output.info("Tweet posted successfully")
    except tweepy.TweepError as e:
        tome_output = TomeOutput()
        tome_output.error(f"Failed to post tweet: {e.reason}")
