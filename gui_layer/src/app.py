import os
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

try:
    from gui_layer.src.question_panel import InspectionPanel
except ModuleNotFoundError:
    sys.path.append(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    )
    from gui_layer.src.question_panel import InspectionPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window with Embedded Panel")
        self.setGeometry(200, 200, 600, 400)

        # Add InspectionPanel as part of the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        self.inspection_panel = InspectionPanel()
        layout.addWidget(self.inspection_panel)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())