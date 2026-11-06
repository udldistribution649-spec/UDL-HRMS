import getpass
import psycopg

password = getpass.getpass("HRMS database password: ")

try:
    with psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="udl_hrms_db",
        user="udl_hrms_app",
        password=password,
        connect_timeout=5
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    current_database(),
                    current_user,
                    current_setting('server_version')
            """)
            print("Database connection successful!")
            print("Database, User, Version:", cursor.fetchone())

except Exception as error:
    print("Database connection failed:", error)
