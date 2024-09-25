import os
import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QDialog,
    QSlider,
    QComboBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QAction


try:
    from gui_layer.src.question_panel import InspectionPanel
    from gui_layer.src.login_dialog import LoginDialog
    from gui_layer.src.side_edit_panel import SideEditPanel
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from gui_layer.src.question_panel import InspectionPanel
    from gui_layer.src.login_dialog import LoginDialog
    from gui_layer.src.side_edit_panel import SideEditPanel


class Settings:
    """
    Class to manage global settings for contrast and font size.
    """

    def __init__(self):
        self.contrast = 100  # Default contrast level (100%)
        self.font_size = 12

    def apply_settings(self, widget):
        """
        Apply the settings to a widget and its children recursively.
        :param widget: QWidget or QMainWindow to apply settings to.
        """
        font = widget.font()
        font.setPointSize(self.font_size)
        widget.setFont(font)

        palette = widget.palette()
        palette.setColor(widget.backgroundRole(), self.get_contrast_color())
        widget.setPalette(palette)

        for child in widget.findChildren(QWidget):
            self.apply_settings(child)

    def get_contrast_color(self):
        """Adjust the contrast color based on the contrast setting."""
        if self.contrast >= 100:
            # For contrast values >= 100, the color becomes brighter, whiter
            brightness = int(255 * (self.contrast / 150))  # Scale max to 150%
        else:
            # For contrast values < 100, the color becomes darker, more black
            brightness = int(255 * (self.contrast / 100))
        color = QColor(brightness, brightness, brightness)
        return color


class ContrastDialog(QDialog):
    """
    Dialog for adjusting contrast.
    """

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Adjust Contrast")
        self.setGeometry(300, 300, 200, 100)

        layout = QVBoxLayout(self)

        # Slider for adjusting contrast (range: 50-150%)
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(50, 150)
        self.contrast_slider.setValue(self.settings.contrast)
        self.contrast_slider.valueChanged.connect(self.update_contrast)

        layout.addWidget(QLabel("Contrast"))
        layout.addWidget(self.contrast_slider)

    def update_contrast(self, value):
        """Update the contrast setting."""
        self.settings.contrast = value
        self.settings.apply_settings(self.parent())


class FontSizeDialog(QDialog):
    """
    Dialog for adjusting font size.
    """

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Adjust Font Size")
        self.setGeometry(300, 300, 200, 100)

        layout = QVBoxLayout(self)

        # ComboBox for selecting font size
        self.font_size_combo = QComboBox()
        for size in range(8, 25):
            self.font_size_combo.addItem(f"{size} pt")
        self.font_size_combo.setCurrentText(f"{self.settings.font_size} pt")
        self.font_size_combo.currentTextChanged.connect(self.update_font_size)

        layout.addWidget(QLabel("Font Size"))
        layout.addWidget(self.font_size_combo)

    def update_font_size(self, value):
        """Update the font size setting."""
        self.settings.font_size = int(value.split(" ")[0])
        self.settings.apply_settings(self.parent())


class MainWindow(QMainWindow):
    """
    Main window containing both the inspection and site edit panels,
    with settings for adjusting contrast and font size from the application bar.
    """

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setWindowTitle("Main Window with Embedded Panel")
        self.setGeometry(200, 200, 600, 400)

        # Create the menu bar
        menu_bar = self.menuBar()

        # Add "Settings" menu
        settings_menu = menu_bar.addMenu("Settings")

        # Add actions for adjusting contrast and font size
        contrast_action = QAction("Adjust Contrast", self)
        font_size_action = QAction("Adjust Font Size", self)

        contrast_action.triggered.connect(self.open_contrast_dialog)
        font_size_action.triggered.connect(self.open_font_size_dialog)

        settings_menu.addAction(contrast_action)
        settings_menu.addAction(font_size_action)

        # Central widget layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)

        # Layout for other elements
        top_layout = QHBoxLayout()

        # Buttons for switching panels
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
        self.side_edit_panel.site_changed.connect(
            self.inspection_panel.load_sides
        )

        # Logout functionality
        self.logout_button.clicked.connect(self.logout)
        # Apply initial settings
        self.settings.apply_settings(self)

    def open_contrast_dialog(self):
        """Open the contrast adjustment dialog."""
        contrast_dialog = ContrastDialog(self.settings, self)
        contrast_dialog.exec()

    def open_font_size_dialog(self):
        """Open the font size adjustment dialog."""
        font_size_dialog = FontSizeDialog(self.settings, self)
        font_size_dialog.exec()

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
        self.stack.setCurrentWidget(self.inspection_panel)

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
    settings = Settings()
    window = MainWindow(settings)
    window.show()
    sys.exit(app.exec())
