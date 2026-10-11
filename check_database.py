
import database
from database import get_connection, get_player

print("Database path:", database.DB_PATH)

connection = get_connection()

tables = connection.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

print("TABLES:", [row[0] for row in tables])

print(
    "PLAYERS:",
    connection.execute("SELECT COUNT(*) FROM players").fetchone()[0]
)

print(
    "MISSIONS:",
    connection.execute(
        "SELECT COUNT(*) FROM mission_completions"
    ).fetchone()[0]
)

print("TEST PLAYER:", get_player(1))

connection.close()
