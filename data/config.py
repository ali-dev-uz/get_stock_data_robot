from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Bot token
ADMINS = env.list("ADMINS")  # list of admins
IP = env.str("IP")  # The host ip address
TWELVE_API = env.str("TWELVE_API")  # POLYGON API key
DB_USER = env.str("DB_USER")
TICKER = env.str("TICKER")
CHANNEL = env.int("CHANNEL")
DB_PASS = env.str("DB_PASS")
DB_NAME = env.str("DB_NAME")
DB_HOST = env.str("DB_HOST")
FILE_PATH = env.str("FILE_PATH")
