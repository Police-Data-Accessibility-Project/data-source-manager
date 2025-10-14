from discord_poster import DiscordPoster
from environs import Env

def test_post_to_discord():
    env = Env()
    env.read_env()
    dp = DiscordPoster(
        webhook_url=env.str("PROD_DISCORD_WEBHOOK_URL")
    )
    dp.post_to_discord("Testing")