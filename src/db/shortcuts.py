async def write_user(
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
    with engine.connect() as conn:
        create_user = insert(user_table).values(
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

        conn.execute(create_user)
        session.commit()
        return uuid, access_token


def user_exists(tg_id):
    with engine.connect() as conn:
        q = session.query(exists().where(User.tg_id == tg_id)).scalar()
        return q


def user_banned(tg_id):
    with engine.connect() as conn:
        q = select(user_table).where(user_table.c.tg_id == tg_id)
        user = conn.execute(q).first()
        return user is not None and user.is_banned


def get_user(tg_id):
    with engine.connect() as conn:
        q = select(user_table).where(user_table.c.tg_id == tg_id)
        return conn.execute(q).first()


def add_user_violation(
        tg_id,
        violation_type
):
    with engine.connect() as conn:
        user = get_user(tg_id)
        conn.execute(
            insert(violation_table).values(
                type=violation_type,
                client_id=user.uuid
            )
        )
        session.commit()


def is_user_under_investigation(
        tg_id,
):
    with engine.connect() as conn:
        user = get_user(tg_id)
        return user.under_investigation


def increase_user_error_count(
        tg_id
):
    with engine.connect() as conn:
        user = get_user(tg_id)
        q = update(user_table).where(user_table.c.tg_id == tg_id).values(
            error_count=user_table.c.error_count + 1,
            karma=user_table.c.karma - 1,
            verification_probability=min(user.verification_probability + 0.2, 0.8)
        )
        conn.execute(q)
        session.commit()


def increase_user_correct_count(
        tg_id
):
    with engine.connect() as conn:
        user = get_user(tg_id)
        q = update(user_table).where(user_table.c.tg_id == tg_id).values(
            correct_count=user_table.c.correct_count + 1,
            karma=user_table.c.karma + 1,
            verification_probability=max(user.verification_probability - 0.2, 0.15)
        )
        conn.execute(q)
        session.commit()


def user_validated_now(
        tg_id,
):
    with engine.connect() as conn:
        q = update(user_table).where(user_table.c.tg_id == tg_id).values(
            last_validated_at=datetime.now()
        )
        conn.execute(q)
        session.commit()


def get_all_users():
    with engine.connect() as conn:
        q = select(user_table)
        return conn.execute(q).fetchall()


async def edit_profile(tg_id, age=None, lang=None, accent=None):
    with engine.connect() as conn:
        if age is not None:
            q = update(user_table).where(user_table.c.tg_id == tg_id).values(
                year_of_birth=age
            )
        elif lang is not None:
            q = update(user_table).where(user_table.c.tg_id == tg_id).values(
                native_language=lang
            )
        elif accent is not None:
            q = update(user_table).where(user_table.c.tg_id == tg_id).values(
                accent_region=accent
            )
        conn.execute(q)
        session.commit()