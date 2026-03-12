import psycopg2


def get_db():

    conn = psycopg2.connect(
        host="localhost",
        database="pulseguard",
        user="pulse",
        password="pulse",
        port=5432
    )

    return conn