"""
services/auth_service.py
Handles authentication: login, registration, password hashing via bcrypt.
Uses psycopg2 (%s placeholders).
"""
import bcrypt
from typing import Optional, Tuple

from database.connection import get_conn
from models.user import User
from config.settings import settings


class AuthService:

    def login(self, username: str, password: str) -> Optional[User]:
        """Verify credentials and return User on success, None on failure."""
        if not username or not password:
            return None
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM users WHERE username = %s AND is_active = 1",
                (username,)
            )
            row = cur.fetchone()
            if row and bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
                return User.from_row(row)
            return None
        finally:
            conn.close()

    def register(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Register a new user.
        Returns (success: bool, message: str).
        """
        if len(username) < settings.MIN_USERNAME_LENGTH:
            return False, f"Username must be at least {settings.MIN_USERNAME_LENGTH} characters."
        if len(password) < settings.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters."

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hashed),
            )
            conn.commit()
            return True, "Account created successfully."
        except Exception:
            conn.rollback()
            return False, "Username already exists."
        finally:
            conn.close()

    def list_users(self) -> list:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE is_active = 1 ORDER BY username")
            return [User.from_row(r) for r in cur.fetchall()]
        finally:
            conn.close()


auth_service = AuthService()
