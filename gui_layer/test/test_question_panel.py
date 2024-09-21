import os
import sys

import pytest
from PySide6.QtWidgets import QApplication

try:
    from gui_layer.src.question_panel import InspectionPanel
except ModuleNotFoundError:
    sys.path.append(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    )
    from gui_layer.src.question_panel import InspectionPanel

# Ensure there is only one QApplication instance for the test session
@pytest.fixture(scope="session")
def app():
    """Set up a Qt application for testing."""
    app = QApplication.instance()  # Reuse existing instance if it exists
    if app is None:
        app = QApplication([])  # Create a new instance if not
    yield app  # Yield it for use across tests


def test_load_sides(app, qtbot):
    """
    Test that the sides are loaded correctly into the dropdown.
    
    Ensure the panel loads sides
    correctly from the SQLite database.
    """
    panel = InspectionPanel()
    qtbot.addWidget(panel)

    # Check if sides are loaded in the dropdown
    assert panel.side_dropdown.count() > 1  # Includes "Select Side"


def test_update_questions(app, qtbot):
    """
    Test that the questions are updated when a side is selected.

    Ensure that when a side is selected, the corresponding questions
    are loaded in the form layout.
    """
    panel = InspectionPanel()
    qtbot.addWidget(panel)

    # Select the second side in the dropdown (assuming valid data)
    panel.side_dropdown.setCurrentIndex(1)

    # Simulate the update of questions
    panel.update_questions()

    # Check that at least one question is added to the form layout
    assert len(panel.question_labels) > 0
    assert len(panel.answer_fields) > 0
