import os


class Config:

    SECRET_KEY = "bps-tidore"


    SQLALCHEMY_DATABASE_URI = (
        os.getenv("DATABASE_URL")
        or "postgresql://neondb_owner:npg_xsKALz7Y2MJy@ep-still-rice-ah5w9rta.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
    )


    SQLALCHEMY_TRACK_MODIFICATIONS = False


    SQLALCHEMY_ENGINE_OPTIONS = {

        "pool_pre_ping": True,

        "pool_recycle": 300,

        "pool_timeout": 30

    }