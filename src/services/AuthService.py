from src.database.db_connection import get_db
from src.services.UserDataLocal import UserDataLocal
from src.models.Session import Session

class AuthService:
    def __init__(self):
        self.current_session = None
        self.user_data_local = UserDataLocal()

    def validate_credentials(self, username, password):
        user = self.user_data_local.find_by_username(username)
        if user is None:
            return False
        if not self._verify_password(password, user.password):
            return False
        self.current_session = Session()
        self.current_session.create_session(user)
        self._save_session()
        return True

    def _verify_password(self, input_password, stored_password):
        return input_password == stored_password

    def logout(self, session_id):
        if self.current_session:
            self.current_session.invalidate()
            self._end_session(session_id)
            self.current_session = None

    def is_authenticated(self):
        return (self.current_session is not None
                and self.current_session.is_active)

    def get_current_user(self):
        if self.current_session:
            return self.current_session.logged_in_user
        return None

    def get_current_session(self):
        return self.current_session

    def _save_session(self):
        db = get_db()
        cur = db.connection.cursor()
        cur.execute(
            "INSERT INTO sessions (session_id, user_id, login_time, is_active) VALUES (%s, %s, %s, %s)",
            (self.current_session.session_id,
             self.current_session.logged_in_user.user_id,
             self.current_session.login_time,
             True)
        )
        db.connection.commit()
        cur.close()

    def _end_session(self, session_id):
        db = get_db()
        cur = db.connection.cursor()
        cur.execute(
            "UPDATE sessions SET is_active = FALSE WHERE session_id = %s",
            (session_id,)
        )
        db.connection.commit()
        cur.close()
