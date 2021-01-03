import os
from pathlib import Path

import dotenv

CWD = Path(__file__).parent
ENV = CWD.joinpath(".env")
dotenv.load_dotenv(ENV)

# General
PORT = int(os.getenv("mealie_port", 9000))

# Mongo Database
MEALIE_DB_NAME = os.getenv("mealie_db_name", "mealie")
DB_USERNAME = os.getenv("db_username", "root")
DB_PASSWORD = os.getenv("db_password", "example")
DB_HOST = os.getenv("db_host", "mongo")
DB_PORT = os.getenv("db_port", 27017)

# SFTP Email Stuff
SFTP_USERNAME = os.getenv("sftp_username", None)
SFTP_PASSWORD = os.getenv("sftp_password", None)
