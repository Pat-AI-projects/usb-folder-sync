import sys

from PySide6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                               QLineEdit, QMainWindow, QMessageBox, QPushButton,
                               QPlainTextEdit, QVBoxLayout, QWidget)

from . import adb, engine


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("USB Folder Sync")
        central = QWidget()
        layout = QVBoxLayout(central)

        pc_row = QHBoxLayout()
        self.pc_edit = QLineEdit()
        pc_button = QPushButton("Browse...")
        pc_button.clicked.connect(self.pick_pc)
        pc_row.addWidget(QLabel("PC folder:"))
        pc_row.addWidget(self.pc_edit, 1)
        pc_row.addWidget(pc_button)
        layout.addLayout(pc_row)

        phone_row = QHBoxLayout()
        self.phone_edit = QLineEdit("/sdcard/Sync")
        phone_row.addWidget(QLabel("Phone folder:"))
        phone_row.addWidget(self.phone_edit, 1)
        layout.addLayout(phone_row)

        self.sync_button = QPushButton("Sync now")
        self.sync_button.clicked.connect(self.sync_now)
        layout.addWidget(self.sync_button)

        self.report = QPlainTextEdit()
        self.report.setReadOnly(True)
        layout.addWidget(self.report)

        self.setCentralWidget(central)

    def pick_pc(self):
        path = QFileDialog.getExistingDirectory(self, "Choose PC folder")
        if path:
            self.pc_edit.setText(path)

    def decide(self, rel, reason):
        box = QMessageBox(self)
        box.setWindowTitle("Sync decision needed")
        box.setText(f"{rel}\n{reason}")
        pc = box.addButton("Use PC version", QMessageBox.ButtonRole.AcceptRole)
        phone = box.addButton("Use phone version", QMessageBox.ButtonRole.AcceptRole)
        copy = box.addButton("Copy to other device", QMessageBox.ButtonRole.AcceptRole)
        box.addButton("Skip", QMessageBox.ButtonRole.RejectRole)
        box.exec()
        clicked = box.clickedButton()
        if clicked is pc:
            return "pc"
        if clicked is phone:
            return "phone"
        if clicked is copy:
            return "copy"
        return "skip"

    def sync_now(self):
        local_root = self.pc_edit.text().strip()
        remote_root = self.phone_edit.text().strip()
        if not local_root or not remote_root:
            QMessageBox.warning(self, "Missing folder", "Choose both the PC folder and the phone folder.")
            return
        try:
            ok, drift = engine.check_clocks()
        except adb.AdbError as exc:
            QMessageBox.critical(self, "USB error", str(exc))
            return
        if not ok:
            QMessageBox.warning(
                self, "Clocks not synchronized",
                f"PC and phone clocks differ by {drift:.0f}s "
                f"(tolerance {engine.CLOCK_TOLERANCE_SECONDS}s). Sync aborted.")
            return
        try:
            report = engine.plan_sync(local_root, remote_root, self.decide)
            engine.execute(local_root, remote_root, report)
        except adb.AdbError as exc:
            QMessageBox.critical(self, "Sync failed", str(exc))
            return
        lines = [f"{item.action.upper():5} {item.path} - {item.detail}" for item in report]
        self.report.setPlainText("\n".join(lines) if lines else "Nothing to do.")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
