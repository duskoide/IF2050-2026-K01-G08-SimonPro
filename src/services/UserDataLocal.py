from src.database.db_connection import get_db
from src.models.User import User

class UserDataLocal:
    def __init__(self):
        self.users = []
        self._load_users()

    def _load_users(self):
        db   = get_db()
        rows = db.execute_query(
            "SELECT user_id, username, password, role FROM users"
        )
        self.users = [
            User(row["user_id"], row["username"], row["password"], row["role"])
            for row in rows
        ]

    def find_by_username(self, username):
        for user in self.users:
            if user.username == username:
                return user
        return None