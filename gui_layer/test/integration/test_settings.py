import os
import sys

import pytest
from pytest_bdd import scenarios, given, when, then
from PySide6.QtWidgets import QApplication, QMainWindow
from gui_layer.src.app import MainWindow, Settings


try:
    from gui_layer.src.app import MainWindow, Settings
except ModuleNotFoundError:
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    )
    from gui_layer.src.app import MainWindow, Settings

scenarios("./test_settings.feature")


@pytest.fixture
def app():
    """Create a fixture for the QApplication instance."""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"  # Enable headless mode
    app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def main_window(app):
    """Fixture for the main window."""
    settings = Settings()
    main_window = MainWindow(settings)
    main_window.show()
    return main_window


@given("the application is started")
def app_started(main_window):
    """
    Ensure the application has started and the main window is shown.

    :param main_window: The main window of the application.
    """
    assert isinstance(main_window, QMainWindow)
    assert main_window.isVisible()


@when("I open the settings menu")
def open_settings_menu(main_window):
    """
    Simulate opening the settings menu.

    :param main_window: The main window of the application.
    """
    menu_bar = main_window.menuBar()
    settings_menu = menu_bar.actions()[0]
    assert settings_menu.text() == "Settings"


@when("I adjust the contrast to 150")
def adjust_contrast(main_window):
    """
    Adjust the contrast setting using the dialog.

    :param main_window: The main window of the application.
    """
    settings = main_window.settings
    settings.contrast = 150
    settings.apply_settings(main_window)


@then("the colors of the application should whiten")
def check_whitened_contrast(main_window):
    """
    Verify that the contrast setting has resulted in a whitening effect.

    :param main_window: The main window of the application.
    """
    color = main_window.settings.get_contrast_color()

    # Check that the color has whitened (closer to 255 for all channels)
    assert color.red() > 200
    assert color.green() > 200
    assert color.blue() > 200
    assert color.alpha() == 255  # Ensure the alpha value is also fully opaque


@when("I adjust the font size to 20")
def adjust_font_size(main_window):
    """
    Adjust the font size setting using the dialog.

    :param main_window: The main window of the application.
    """
    settings = main_window.settings
    settings.font_size = 20
    settings.apply_settings(main_window)


@then("the font size across the application should increase")
def check_increased_font_size(main_window):
    """
    Verify that the font size has increased across the application.

    :param main_window: The main window of the application.
    """
    font = main_window.font()
    assert font.pointSize() > 12
