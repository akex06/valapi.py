import random
import sqlite3


class Database:
    def __init__(self, fp: str = "database.sqlite3") -> None:
        self.conn = sqlite3.connect(fp)
        self.c = self.conn.cursor()

        self._create_tables()

    def _create_tables(self) -> None:
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS otp_codes (
                player_id TEXT,
                code INTEGER,
                PRIMARY KEY (player_id, code)
            );
        """)
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS account_links (
                player_id TEXT,
                user_id INTEGER,
                PRIMARY KEY (player_id, user_id)
            );
        """)

        self.c.execute("""
            CREATE TABLE IF NOT EXISTS channel_links (
                player_id TEXT,
                channel_id INTEGER,
                PRIMARY KEY (player_id, channel_id)
            );
        """)

        self.conn.commit()

    def get_user_id(self, player_id: str) -> int | None:
        user_id = self.c.execute(
            "SELECT user_id FROM account_links WHERE player_id = ?",
            (player_id,)
        ).fetchone()
        print(user_id, player_id)
        return user_id[0] if user_id else None

    def get_player_id(self, user_id: int) -> str | None:
        player_id = self.c.execute(
            "SELECT player_id FROM account_links WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        return player_id[0] if player_id else None

    def add_account_link(self, player_id: str, user_id: int) -> None:
        exists = self.c.execute(
            "SELECT 1 FROM account_links WHERE player_id = ? AND user_id = ?",
            (player_id, user_id)
        ).fetchone()
        if exists:
            raise ValueError("Account link already exists")

        self.c.execute("INSERT INTO account_links (player_id, user_id) VALUES (?, ?)", (player_id, user_id))
        self.conn.commit()

    def update_account_link(self, player_id: str, user_id: int) -> None:
        if self.get_user_id(player_id) is None:
            raise ValueError("The specified player id is not linked")

        self.c.execute("UPDATE account_links SET user_id = ? WHERE player_id=?", (user_id, player_id))
        self.conn.commit()

    def delete_account_link(self, player_id: str) -> None:
        self.c.execute("DELETE FROM account_links WHERE player_id=?", (player_id,))
        self.conn.commit()

    def get_channel_id(self, player_id: str) -> int | None:
        channel = self.c.execute("SELECT channel_id FROM channel_links WHERE player_id = ?", (player_id,)).fetchone()
        if channel:
            return channel[0]

        return None

    def set_channel_link(self, user_id: int, channel_id: int) -> None:
        player_id = self.get_player_id(user_id)
        channel = self.get_channel_id(player_id)

        if channel:
            self.c.execute("UPDATE channel_links SET channel_id = ? WHERE player_id = ?", (player_id, channel_id))
        else:
            self.c.execute("INSERT INTO channel_links (player_id, channel_id) VALUES (?, ?)", (player_id, channel_id))

        self.conn.commit()

    def get_codes(self) -> list[int]:
        return self.c.execute("SELECT code FROM otp_codes").fetchall()

    def get_random_code(self) -> int:
        codes = map(lambda x: x[0], self.get_codes())
        return random.choice(list(filter(lambda x: x not in codes, range(0, 1_000_000))))

    def set_otp_code(self, player_id: str) -> int:
        code = self.get_random_code()
        self.c.execute("INSERT INTO otp_codes (player_id, code) VALUES (?, ?)", (player_id, code))
        self.conn.commit()

        return code

    def get_otp_code(self, player_id: str) -> int:
        otp_code = self.c.execute(
            "SELECT code FROM otp_codes WHERE player_id = ?",
            (player_id,)
        ).fetchone()

        if otp_code:
            return otp_code[0]

        return self.set_otp_code(player_id)

    def is_code_valid(self, code: int) -> str | None:
        """
        Check if the otp code provided is valid, returns the player id or None

        :param code: The OTP code
        :return: the player id or None if ti was not found
        """
        player_id = self.c.execute(
            "SELECT player_id FROM otp_codes WHERE code = ?",
            (code,)
        ).fetchone()

        if player_id:
            return player_id[0]

        return None

    def delete_code(self, player_id: str) -> None:
        self.c.execute("DELETE FROM otp_codes WHERE player_id = ?", (player_id,))
        self.conn.commit()
