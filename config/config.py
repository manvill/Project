import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        env_file = f".env.{os.getenv('ENV', 'local')}"
        load_dotenv(dotenv_path=env_file)
        self.dexscreener_api_url = os.getenv("DEXSCREENER_API_URL")
        self.database_path = os.getenv("DATABASE_PATH", "tokens.db")