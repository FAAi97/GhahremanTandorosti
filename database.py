
import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "game.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_db():
    with get_connection() as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                xp INTEGER NOT NULL DEFAULT 0,
                coins INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS mission_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                mission_id TEXT NOT NULL,
                completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                correct_count INTEGER NOT NULL DEFAULT 0,
                total_questions INTEGER NOT NULL DEFAULT 0,
                xp_awarded INTEGER NOT NULL DEFAULT 0,
                coins_awarded INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(player_id) REFERENCES players(id),
                UNIQUE(player_id, mission_id)
            );

            CREATE TABLE IF NOT EXISTS habit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                habit_id TEXT NOT NULL,
                log_date TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY(player_id) REFERENCES players(id),
                UNIQUE(player_id, habit_id, log_date)
            );

            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                item_id TEXT NOT NULL,
                purchased_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(player_id) REFERENCES players(id),
                UNIQUE(player_id, item_id)
            );
        """)


def get_or_create_player(username):
    username = username.strip()

    if not username:
        raise ValueError("نام بازیکن نمی‌تواند خالی باشد.")

    with get_connection() as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO players (username)
            VALUES (?)
            """,
            (username,)
        )

        player = connection.execute(
            "SELECT * FROM players WHERE username = ?",
            (username,)
        ).fetchone()

        return dict(player)


def get_player(player_id):
    with get_connection() as connection:
        player = connection.execute(
            "SELECT * FROM players WHERE id = ?",
            (player_id,)
        ).fetchone()

        return dict(player) if player else None


def get_completed_missions(player_id):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT mission_id
            FROM mission_completions
            WHERE player_id = ?
            """,
            (player_id,)
        ).fetchall()

        return {row["mission_id"] for row in rows}


def complete_mission(
    player_id,
    mission_id,
    correct_count,
    total_questions,
    xp_awarded,
    coins_awarded,
):
    """
    مأموریت را فقط یک بار ثبت می‌کند.
    اگر قبلاً ثبت شده باشد، جایزه دوباره داده نمی‌شود.
    """

    with get_connection() as connection:
        try:
            connection.execute("BEGIN IMMEDIATE")

            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO mission_completions (
                    player_id,
                    mission_id,
                    correct_count,
                    total_questions,
                    xp_awarded,
                    coins_awarded
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    player_id,
                    mission_id,
                    correct_count,
                    total_questions,
                    xp_awarded,
                    coins_awarded,
                )
            )

            if cursor.rowcount == 0:
                connection.rollback()
                return False

            connection.execute(
                """
                UPDATE players
                SET xp = xp + ?, coins = coins + ?
                WHERE id = ?
                """,
                (xp_awarded, coins_awarded, player_id)
            )

            connection.commit()
            return True

        except Exception:
            connection.rollback()
            raise


def get_habits_for_date(player_id, log_date=None):
    if log_date is None:
        log_date = date.today().isoformat()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT habit_id, completed
            FROM habit_logs
            WHERE player_id = ? AND log_date = ?
            """,
            (player_id, log_date)
        ).fetchall()

        return {
            row["habit_id"]: bool(row["completed"])
            for row in rows
        }


def save_habit(player_id, habit_id, completed, log_date=None):
    if log_date is None:
        log_date = date.today().isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO habit_logs (
                player_id, habit_id, log_date, completed
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(player_id, habit_id, log_date)
            DO UPDATE SET completed = excluded.completed
            """,
            (player_id, habit_id, log_date, int(completed))
        )


def get_purchases(player_id):
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT item_id FROM purchases WHERE player_id = ?",
            (player_id,)
        ).fetchall()

        return {row["item_id"] for row in rows}


def buy_item(player_id, item_id, price):
    """
    خرید آیتم و کم‌کردن سکه در یک تراکنش انجام می‌شود.
    آیتم تکراری یا خرید بدون سکه کافی پذیرفته نمی‌شود.
    """

    with get_connection() as connection:
        try:
            connection.execute("BEGIN IMMEDIATE")

            player = connection.execute(
                "SELECT coins FROM players WHERE id = ?",
                (player_id,)
            ).fetchone()

            if player is None or player["coins"] < price:
                connection.rollback()
                return False

            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO purchases (player_id, item_id)
                VALUES (?, ?)
                """,
                (player_id, item_id)
            )

            if cursor.rowcount == 0:
                connection.rollback()
                return False

            connection.execute(
                """
                UPDATE players
                SET coins = coins - ?
                WHERE id = ?
                """,
                (price, player_id)
            )

            connection.commit()
            return True

        except Exception:
            connection.rollback()
            raise


init_db()
