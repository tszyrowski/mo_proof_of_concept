from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QInputDialog,
)
import sqlite3


class SideEditPanel(QWidget):
    """
    Panel for adding, editing, and deleting sides in the SQLite database.

    This panel provides a table view of all sides and allows the user
    to search, add, edit, and delete sides.

    Signals
    -------
    site_changed : Signal
        Emitted when a site is added, edited, or deleted.
    """

    site_changed = Signal()  # Signal to notify when a site is modified

    def __init__(self):
        """Initialize the SideEditPanel."""
        super().__init__()
        self.setWindowTitle("Side Edit Panel")
        self.setGeometry(100, 100, 600, 400)

        # Main layout
        self.layout = QVBoxLayout()

        # Search bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search for a side...")
        self.search_bar.textChanged.connect(self.search_sides)
        self.layout.addWidget(self.search_bar)

        # Table for displaying sides
        self.sides_table = QTableWidget(self)
        self.sides_table.setColumnCount(1)
        self.sides_table.setHorizontalHeaderLabels(["Side Name"])
        self.layout.addWidget(self.sides_table)

        # Buttons to add, edit, and delete sides
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Side", self)
        self.edit_button = QPushButton("Edit Side", self)
        self.delete_button = QPushButton("Delete Side", self)

        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)

        self.layout.addLayout(buttons_layout)

        # Connect buttons
        self.add_button.clicked.connect(self.add_side)
        self.edit_button.clicked.connect(self.edit_side)
        self.delete_button.clicked.connect(self.delete_side)

        self.setLayout(self.layout)

        # Load sides from the database
        self.load_sides()

    def load_sides(self):
        """Load all sides from the database and display them in the table."""
        conn = sqlite3.connect("inspection_data.db")
        c = conn.cursor()
        c.execute("SELECT side_name FROM sides")
        sides = c.fetchall()
        conn.close()

        self.sides_table.setRowCount(0)  # Clear the table
        for row, side in enumerate(sides):
            self.sides_table.insertRow(row)
            self.sides_table.setItem(row, 0, QTableWidgetItem(side[0]))

    def search_sides(self):
        """Filter sides in the table based on the search query."""
        query = self.search_bar.text().lower()
        for row in range(self.sides_table.rowCount()):
            side_name = self.sides_table.item(row, 0).text().lower()
            self.sides_table.setRowHidden(row, query not in side_name)

    def add_side(self):
        """Open a dialog to add a new side."""
        side_name, ok = QInputDialog.getText(
            self, "Add Side", "Enter side name:"
        )
        if ok and side_name:
            conn = sqlite3.connect("inspection_data.db")
            c = conn.cursor()
            c.execute("INSERT INTO sides (side_name) VALUES (?)", (side_name,))
            conn.commit()
            conn.close()
            self.load_sides()  # Reload sides after adding
            self.site_changed.emit()  # Emit the signal

    def edit_side(self):
        """Edit the currently selected side."""
        current_row = self.sides_table.currentRow()
        if current_row == -1:
            return  # No side selected

        side_name = self.sides_table.item(current_row, 0).text()
        new_name, ok = QInputDialog.getText(
            self, "Edit Side", "Edit side name:", text=side_name
        )
        if ok and new_name:
            conn = sqlite3.connect("inspection_data.db")
            c = conn.cursor()
            c.execute(
                "UPDATE sides SET side_name=? WHERE side_name=?",
                (new_name, side_name),
            )
            conn.commit()
            conn.close()
            self.load_sides()  # Reload sides after editing
            self.site_changed.emit()  # Emit the signal

    def delete_side(self):
        """Delete the currently selected side."""
        current_row = self.sides_table.currentRow()
        if current_row == -1:
            return  # No side selected

        side_name = self.sides_table.item(current_row, 0).text()
        confirm, ok = QInputDialog.getText(
            self, "Delete Side", f"Delete side: {side_name}? (yes/no)"
        )
        if ok and confirm.lower() == "yes":
            conn = sqlite3.connect("inspection_data.db")
            c = conn.cursor()
            c.execute("DELETE FROM sides WHERE side_name=?", (side_name,))
            conn.commit()
            conn.close()
            self.load_sides()  # Reload sides after deleting
            self.site_changed.emit()  # Emit the signal
