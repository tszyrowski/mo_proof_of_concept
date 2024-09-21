import os
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QStackedWidget, QCheckBox, QHBoxLayout, QLabel
)

try:
    from gui_layer.src.question_panel import InspectionPanel
    from gui_layer.src.login_dialog import LoginDialog
    from gui_layer.src.side_edit_panel import SideEditPanel
except ModuleNotFoundError:
    sys.path.append(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    )
    from gui_layer.src.question_panel import InspectionPanel
    from gui_layer.src.login_dialog import LoginDialog
    from gui_layer.src.side_edit_panel import SideEditPanel


class MainWindow(QMainWindow):
    """
    Main window containing both the inspection and site edit panels.

    The window allows users to switch between embedded panels or 
    open them in a new window using a checkbox. Access to the 
    side edit panel requires admin login.
    """
    
    def __init__(self):
        """Initialize the main window layout and widgets."""
        super().__init__()
        self.setWindowTitle("Main Window with Embedded Panel")
        self.setGeometry(200, 200, 600, 400)

        # Central widget layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)

        # Layout for the buttons and checkbox
        top_layout = QHBoxLayout()

        # Buttons to switch between panels
        self.switch_to_inspection_button = QPushButton("Inspection Panel")
        self.switch_to_side_edit_button = QPushButton("Site Edit Panel")
        self.new_window_checkbox = QCheckBox("Open in New Window")

        # Login message and logout button
        self.login_message = QLabel("")
        self.logout_button = QPushButton("Logout")
        self.logout_button.setVisible(False)

        top_layout.addWidget(self.switch_to_inspection_button)
        top_layout.addWidget(self.switch_to_side_edit_button)
        top_layout.addWidget(self.new_window_checkbox)
        top_layout.addWidget(self.login_message)
        top_layout.addWidget(self.logout_button)

        main_layout.addLayout(top_layout)

        # Stack of different panels (inspection panel and side edit panel)
        self.stack = QStackedWidget()
        self.inspection_panel = InspectionPanel()
        self.side_edit_panel = SideEditPanel()

        self.stack.addWidget(self.inspection_panel)
        self.stack.addWidget(self.side_edit_panel)

        main_layout.addWidget(self.stack)

        # Connect buttons to the single handle function
        self.switch_to_inspection_button.clicked.connect(
            lambda: self.handle_panel(self.inspection_panel, "Inspection Panel")
        )
        self.switch_to_side_edit_button.clicked.connect(self.handle_login)

        # Connect signal to refresh InspectionPanel when a site is changed
        self.side_edit_panel.site_changed.connect(self.inspection_panel.load_sides)

        # Logout functionality
        self.logout_button.clicked.connect(self.logout)

    def handle_login(self):
        """
        Handle the login process when the Site Edit Panel is accessed.

        If the user is not logged in, show the login dialog.
        """
        login_dialog = LoginDialog()
        if login_dialog.exec():  # If login is successful
            self.login_message.setText("Logged in as Admin")
            self.switch_to_side_edit_button.setEnabled(True)
            self.logout_button.setVisible(True)
            self.handle_panel(self.side_edit_panel, "Site Edit Panel")

    def logout(self):
        """
        Handle the logout process by disabling access to the Site Edit Panel.
        """
        self.login_message.setText("")
        self.logout_button.setVisible(False)
        self.side_edit_panel.setEnabled(False) 
        self.stack.setCurrentWidget(self.inspection_panel)  # Switch to inspection panel

    def handle_panel(self, panel, panel_name):
        """
        Handle the action for displaying the panel.

        This function either embeds the panel in the main window or 
        opens it in a new window, based on the checkbox state.

        :param panel: The panel widget to be shown.
        :param panel_name: Title for the panel when opening in a new window.
        """
        if self.new_window_checkbox.isChecked():
            self.open_new_window(panel, panel_name)
        else:
            self.stack.setCurrentWidget(panel)

    def open_new_window(self, panel, title):
        """
        Open the given widget in a new window by creating a copy.

        :param panel: QWidget to display in the new window.
        :param title: Title for the new window.
        """
        new_panel = panel.__class__()  # Create a new instance
        new_window = QMainWindow(self)
        new_window.setWindowTitle(title)
        new_window.setGeometry(300, 300, 600, 400)
        new_window.setCentralWidget(new_panel)
        new_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
