import sqlite3
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QComboBox, QLabel, QLineEdit,
    QFormLayout,
)


class InspectionPanel(QWidget):
    """
    Inspection panel widget that dynamically loads questions
    based on the selected inspection side from a local SQLite database.
    
    Attributes
    ----------
    layout : QVBoxLayout
        Main layout of the panel.
    side_dropdown : QComboBox
        Dropdown to select the inspection side.
    form_layout : QFormLayout
        Layout to display the questions dynamically.
    question_labels : list
        List of QLabel widgets for questions.
    answer_fields : list
        List of QLineEdit widgets for answers.
    """

    def __init__(self):
        """Initialize the inspection panel."""
        super().__init__()
        self.setWindowTitle('Inspection Panel')
        self.setGeometry(100, 100, 400, 300)

        # Main layout
        self.layout = QVBoxLayout()

        # Dropdown for side selection
        self.side_dropdown = QComboBox()
        self.side_dropdown.addItem("Select Side")
        self.load_sides()
        self.side_dropdown.currentIndexChanged.connect(self.update_questions)

        self.layout.addWidget(self.side_dropdown)

        # Form layout to dynamically load questions
        self.form_layout = QFormLayout()
        self.question_labels = []
        self.answer_fields = []

        self.layout.addLayout(self.form_layout)
        self.setLayout(self.layout)

    def load_sides(self):
        """
        Load available inspection sides from the SQLite database into
        the dropdown.

        This method fetches side names from the 'sides' table and adds
        them as items in the dropdown.
        """
        conn = sqlite3.connect('inspection_data.db')
        c = conn.cursor()
        c.execute("SELECT side_name FROM sides")
        sides = c.fetchall()
        conn.close()

        for side in sides:
            self.side_dropdown.addItem(side[0])

    def update_questions(self):
        """
        Update the panel with dynamic questions based on the selected side.

        This method fetches the questions from the database for the
        selected side and adds corresponding fields to the form layout.
        """
        side_name = self.side_dropdown.currentText()

        if side_name != "Select Side":
            conn = sqlite3.connect('inspection_data.db')
            c = conn.cursor()

            # Fetch side_id
            c.execute("SELECT id FROM sides WHERE side_name=?", (side_name,))
            side_id = c.fetchone()[0]

            # Fetch questions for this side
            c.execute(
                "SELECT question FROM questions WHERE side_id=?", (side_id,)
            )
            questions = c.fetchall()
            conn.close()

            # Clear previous questions and answers
            while self.form_layout.count():
                child = self.form_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # Dynamically add new questions
            for question in questions:
                label = QLabel(question[0])
                answer_field = QLineEdit()

                self.form_layout.addRow(label, answer_field)
                self.question_labels.append(label)
                self.answer_fields.append(answer_field)


def run_standalone_panel():
    """
    Run the inspection panel as a standalone window.

    This function initializes a QApplication and runs the InspectionPanel
    as the main window.
    """
    app = QApplication(sys.argv)
    window = InspectionPanel()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_standalone_panel()
