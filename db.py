from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Railway's Postgres plugin gives a URL starting with "postgres://".
# Newer SQLAlchemy (1.4+) only accepts "postgresql://" and will raise
# on the old prefix. This has probably been silently working so far
# only because of caching/an older pinned version — it will break the
# next time the service rebuilds from a clean install. Fixing it now
# so it doesn't surface as a mystery outage later.
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
