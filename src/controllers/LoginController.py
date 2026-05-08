# src/controllers/login_controller.py
class LoginController:
    def __init__(self, auth_service, login_view, on_login_success):
        self.auth_service     = auth_service
        self.login_view       = login_view
        self.on_login_success = on_login_success

    def login(self, username, password):
        if not username or not password:
            self.login_view.show_error("Username dan password tidak boleh kosong")
            return

        result = self.auth_service.validate_credentials(username, password)
        if result:
            self.on_login_success()
        else:
            self.login_view.show_error("Login gagal! Username atau password salah")