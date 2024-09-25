"""
Handles triggering the sync process and displaying status messages.
"""

import os
import sys
import threading

from PySide6.QtCore import QObject, QTimer, Signal, QThread
from PySide6.QtWidgets import QMessageBox

try:
    from sync_layer.sync_db import sync_databases
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from sync_layer.sync_db import sync_databases

SYNC_TIMEOUT = 20  # Timeout in seconds


class SyncThread(QThread):
    """
    QThread to run the sync process in a separate thread.
    Emits signals for sync success or failure.
    """

    sync_success = Signal()
    sync_failed = Signal(str)

    def run(self):
        """
        Override the run method of QThread to run the sync process.
        This method will be executed in a separate thread.
        """
        try:
            # Perform the sync operation
            sync_databases()
            # Emit success if no exceptions
            self.sync_success.emit()
        except Exception as e:
            # Emit failure if an exception occurs
            self.sync_failed.emit(str(e))


class SyncHandler(QObject):
    """
    Handle the sync with signals for sync success, failure, and timeout.
    """

    sync_success = Signal()
    sync_failed = Signal(str)
    sync_timeout = Signal()

    def __init__(self, window):
        super().__init__()
        self.window = window
        self.sync_thread = None
        self.timeout_timer = QTimer(self)

    def run_sync_with_timeout(self):
        """
        Run the sync process with a timeout. If the sync takes longer than
        the specified timeout, it will trigger a timeout error.
        """
        # Set the timeout timer, ensuring it is stopped correctly
        self.timeout_timer.setSingleShot(True)

        def on_timeout():
            """Handle the timeout by emitting a signal."""
            if self.sync_thread and self.sync_thread.isRunning():
                self.sync_thread.terminate()  # Force terminate (not ideal)
            self.sync_timeout.emit()

        # Connect the timeout timer to the on_timeout function
        self.timeout_timer.timeout.connect(on_timeout)

        # Create the sync thread and connect its signals
        self.sync_thread = SyncThread()
        self.sync_thread.sync_success.connect(self.on_sync_success)
        self.sync_thread.sync_failed.connect(self.on_sync_failed)

        # Start the sync thread and the timer
        self.sync_thread.start()
        self.timeout_timer.start(SYNC_TIMEOUT * 1000)

    def on_sync_success(self):
        """Handle sync success by stopping the timer and emitting success signal."""
        self.timeout_timer.stop()  # Stop the timer upon success
        self.sync_success.emit()

    def on_sync_failed(self, error):
        """Handle sync failure by stopping the timer and emitting failure signal."""
        self.timeout_timer.stop()  # Stop the timer upon failure
        self.sync_failed.emit(error)


def run_sync_with_timeout(window):
    """
    Trigger the DB sync process and display success/failure/timeout messages.
    This method connects the sync handler signals to display the appropriate
    messages in the main window.

    :param window: The main window to display messages.
    """
    sync_handler = SyncHandler(window)

    # Connect signals to message boxes
    sync_handler.sync_success.connect(
        lambda: QMessageBox.information(
            window, "Sync Successful", "DB Sync completed successfully!"
        )
    )
    sync_handler.sync_failed.connect(
        lambda err: QMessageBox.critical(
            window, "Sync Failed", f"Sync failed with error:\n{err}"
        )
    )
    sync_handler.sync_timeout.connect(
        lambda: QMessageBox.warning(
            window,
            "Sync Timeout",
            f"Sync process timed out after {SYNC_TIMEOUT} seconds.",
        )
    )

    # Start the sync process with a timeout
    sync_handler.run_sync_with_timeout()
