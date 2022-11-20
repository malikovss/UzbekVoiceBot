from datetime import datetime

from sqlalchemy import insert, exists, select, update
from sqlalchemy.orm import Session

from . import models


async def write_user(
        session: Session,
        tg_id,
        uuid,
        access_token,
        full_name,
        phone_number,
        gender,
        accent_region,
        year_of_birth,
        native_language
):
    create_user = insert(models.User).values(
        tg_id=tg_id,
        uuid=uuid,
        access_token=access_token,
        full_name=full_name,
        phone_number=phone_number,
        gender=gender,
        accent_region=accent_region,
        year_of_birth=year_of_birth,
        native_language=native_language,
    )

    session.execute(create_user)
    session.commit()
    return uuid, access_token


def user_exists(session: Session, tg_id):
    q = session.query(exists().where(models.User.tg_id == tg_id)).scalar()
    return q


def user_banned(session: Session, tg_id):
    q = select(models.User).where(models.User.tg_id == tg_id)
    user = session.execute(q).scalar()
    return user is not None and user.is_banned


def get_user(session: Session, tg_id):
    q = select(models.User).where(models.User.tg_id == tg_id)
    return session.execute(q).scalar()


def add_user_violation(
        session: Session,
        tg_id,
        violation_type
):
    user = get_user(session, tg_id)
    session.execute(
        insert(models.Violations).values(
            type=violation_type,
            client_id=user.uuid
        )
    )
    session.commit()


def is_user_under_investigation(
        session: Session,
        tg_id,
):
    user = get_user(session, tg_id)
    return user.under_investigation


def increase_user_error_count(
        session: Session,
        tg_id
):
    user = get_user(session, tg_id)
    q = update(models.User).where(models.User.tg_id == tg_id).values(
        error_count=models.User.error_count + 1,
        karma=models.User.karma - 1,
        verification_probability=min(user.verification_probability + 0.2, 0.8)
    )
    session.execute(q)
    session.commit()


def increase_user_correct_count(
        session: Session,
        tg_id
):
    user = get_user(session, tg_id)
    q = update(models.User).where(models.User.tg_id == tg_id).values(
        correct_count=models.User.correct_count + 1,
        karma=models.User.karma + 1,
        verification_probability=max(user.verification_probability - 0.2, 0.15)
    )
    session.execute(q)
    session.commit()


def user_validated_now(
        session: Session,
        tg_id,
):
    q = update(models.User).where(models.User.tg_id == tg_id).values(
        last_validated_at=datetime.now()
    )
    session.execute(q)
    session.commit()


def get_all_users(session: Session):
    return session.execute(select(models.User)).scalars().all()


async def edit_profile(session: Session, tg_id, age=None, lang=None, accent=None):
    query = update(models.User)
    if age is not None:
        query = query.where(models.User.tg_id == tg_id).values(
            year_of_birth=age
        )
    elif lang is not None:
        query = query.where(models.User.tg_id == tg_id).values(
            native_language=lang
        )
    elif accent is not None:
        query = query.where(models.User.tg_id == tg_id).values(
            accent_region=accent
        )
    session.execute(query)
    session.commit()
