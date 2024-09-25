from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
import sqlite3


class LoginDialog(QDialog):
    """
    Login dialog to authenticate admin users.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Login")
        self.setGeometry(300, 300, 300, 150)

        self.layout = QVBoxLayout()

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.check_credentials)

        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)

        self.setLayout(self.layout)

    def check_credentials(self):
        """
        Verify the entered credentials with the database.
        """
        username = self.username_input.text()
        password = self.password_input.text()

        conn = sqlite3.connect("inspection_data.db")
        c = conn.cursor()
        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password),
        )
        result = c.fetchone()
        conn.close()

        if result:
            self.accept()  # Close dialog and return success
        else:
            QMessageBox.warning(
                self, "Error", "Incorrect username or password."
            )
