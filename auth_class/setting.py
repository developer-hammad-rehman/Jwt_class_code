from starlette.config import Config
config = Config('.env')
db_url = config.get("DATABASE_URL" ,  cast=str)