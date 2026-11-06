from sqlalchemy import text

from app.core.database import engine


try:
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    current_database(),
                    current_user,
                    current_setting('server_version')
            """)
        )

        print("SQLAlchemy connection successful!")
        print("Database, User, Version:", result.fetchone())

except Exception as error:
    print("SQLAlchemy connection failed:")
    print(error)

finally:
    engine.dispose()