import sqlalchemy as sa
from sqlalchemy.sql import func

from .base import Base


class User(Base):
    __tablename__ = 'user_account'
    id = sa.Column(sa.BigInteger, primary_key=True)
    tg_id = sa.Column(sa.BigInteger, unique=True)
    verification_probability = sa.Column(sa.Float, default=0.2, nullable=False)
    under_investigation = sa.Column(sa.Boolean, default=False, nullable=False)
    offset_score = sa.Column(sa.BigInteger, default=0, nullable=False)
    karma = sa.Column(sa.BigInteger, default=0, nullable=False)
    correct_count = sa.Column(sa.BigInteger, default=0, nullable=False)
    error_count = sa.Column(sa.BigInteger, default=0, nullable=False)
    uuid = sa.Column(sa.String(40), unique=True)
    access_token = sa.Column(sa.String(40), unique=True)
    full_name = sa.Column(sa.String(300))
    phone_number = sa.Column(sa.String(30))
    sweatshirt_size = sa.Column(sa.String(5))
    gender = sa.Column(sa.String(20))
    accent_region = sa.Column(sa.String(100))
    year_of_birth = sa.Column(sa.String(50), nullable=True)
    native_language = sa.Column(sa.String(100))
    vote_streak_count = sa.Column(sa.BigInteger, nullable=True, default=0)
    is_banned = sa.Column(sa.Boolean, nullable=True, default=False)
    ban_reason = sa.Column(sa.String(300), nullable=True)
    banned_time = sa.Column(sa.DATETIME, nullable=True)
    last_validated_at = sa.Column(sa.DATETIME, nullable=True)


class Violations(Base):
    __tablename__ = 'user_violations'
    id = sa.Column(sa.BigInteger, primary_key=True)
    created_at = sa.Column(sa.DATETIME, nullable=False, server_default=func.now())
    type = sa.Column(sa.String(255))
    client_id = sa.Column(sa.String(36))
