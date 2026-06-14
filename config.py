import os

class Config:
    SECRET_KEY = "bps-tidore"

    SQLALCHEMY_DATABASE_URI = (
        os.getenv("DATABASE_URL")
        or "postgresql://neondb_owner:npg_xsKALz7Y2MJy@ep-still-rice-ah5w9rta.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False