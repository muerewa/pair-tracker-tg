from dataclasses import dataclass
from dotenv import dotenv_values

@dataclass
class PostgresConfig:
    user: str
    password: str
    host: str
    port: int
    name: str
    url: str
    bot_token : str

def load() -> PostgresConfig:
    env = dotenv_values(".env")

    return PostgresConfig(
        user=env.get("DB_USER", "postgres"),
        password=env.get("DB_PASSWORD", "postgres"),
        host=env.get("DB_HOST", "localhost"),
        port=int(env.get("DB_PORT", 5432)),
        name=env.get("DB_NAME", "tracket"),
        url=env.get("DATABASE_URL", ""),
        bot_token=env.get("BOT_TOKEN", "")
    )