import sqlalchemy as sqla
import pandas as pd
from config import postgres

def postgres_connection():
    engine = sqla.create_engine(
        f'postgresql://{postgres["user"]}:{postgres["password"]}@{postgres["host"]}:{postgres["port"]}/{postgres["database"]}')
    return engine.connect()


def db_select(query):
    pass


def db_insert(user_id, user_name, dt, subject, object, description):
    
    txt = f"""
    insert into antisimp.simpings (user_id, user_name, dt, subject, object, description)
    values
    ({user_id}, '{user_name}', '{dt}', '{subject}', '{object}', '{description}')
    """
    query = sqla.text(txt)

    with postgres_connection() as con:
        con.execute(query)
        con.commit()
