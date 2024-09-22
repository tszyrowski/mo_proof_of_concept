import sqlite3
import sys
import os

import pytest
from PySide6.QtWidgets import QApplication

try:
    from gui_layer.src.question_panel import InspectionPanel
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from gui_layer.src.question_panel import InspectionPanel


# Ensure there is only one QApplication instance for the test session
@pytest.fixture(scope="session")
def app():
    """Set up a Qt application for testing."""
    app = QApplication.instance()  # Reuse existing instance if it exists
    if app is None:
        app = QApplication([])  # Create a new instance if not
    yield app  # Yield it for use across tests


@pytest.fixture(scope="function")
def reset_db():
    """
    Reset the SQLite database by removing any test sides added during tests.

    This ensures that each test has a consistent environment.
    """
    conn = sqlite3.connect("inspection_data.db")
    cursor = conn.cursor()

    yield

    # Remove test entries
    cursor.execute("DELETE FROM sides WHERE side_name LIKE 'Test Side%'")
    conn.commit()
    conn.close()


def test_integration_add_side(app, qtbot, reset_db):
    """
    Test that new sides added to the SQLite database are correctly loaded
    into the GUI's dropdown.

    This integration test adds a new side to the actual database and
    verifies that it appears in the InspectionPanel dropdown.
    """
    # Insert a new test side into the actual SQLite database
    conn = sqlite3.connect("inspection_data.db")
    cursor = conn.cursor()

    new_sides = [("Test Side A",), ("Test Side B",)]
    cursor.executemany("INSERT INTO sides (side_name) VALUES (?)", new_sides)

    conn.commit()
    conn.close()

    # Initialize the InspectionPanel
    panel = InspectionPanel()
    qtbot.addWidget(panel)

    # Load sides into the dropdown
    panel.load_sides()

    # Fetch the sides from the dropdown and verify the new sides are present
    dropdown_items = [
        panel.side_dropdown.itemText(i) for i in range(panel.side_dropdown.count())
    ]

    # Assert that both new test sides are in the dropdown
    assert "Test Side A" in dropdown_items
    assert "Test Side B" in dropdown_items
