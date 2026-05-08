from datetime import datetime
import uuid

class Session:
    def __init__(self):
        self.session_id     = None
        self.logged_in_user = None
        self.login_time     = None
        self.is_active      = False

    def create_session(self, user):
        self.session_id     = str(uuid.uuid4())
        self.logged_in_user = user
        self.login_time     = datetime.now()
        self.is_active      = True

    def invalidate(self):
        self.is_active      = False
        self.logged_in_user = None

    def get_user_role(self):
        return self.logged_in_user.role if self.logged_in_user else None