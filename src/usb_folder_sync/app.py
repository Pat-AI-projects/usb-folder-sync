import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QFileDialog, QFrame, QHBoxLayout,
                               QLabel, QLineEdit, QMainWindow, QMessageBox,
                               QPushButton, QPlainTextEdit, QVBoxLayout, QWidget)

from . import adb, engine

STYLESHEET = """
* {
    font-family: "Segoe UI", "Inter", "Helvetica Neue", sans-serif;
}
QMainWindow, QWidget#central {
    background: #0b0f0e;
}
QLabel {
    color: #e6efe9;
    font-size: 13px;
}
QLabel#title {
    color: #ffffff;
    font-size: 22px;
    font-weight: 700;
}
QLabel#subtitle {
    color: #8ba398;
    font-size: 12px;
}
QLabel#status {
    background: #16211c;
    color: #8ba398;
    border-radius: 999px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 600;
}
QLabel#statusOk {
    background: #0e2a1f;
    color: #34d399;
    border-radius: 999px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 600;
}
QLabel#statusWarn {
    background: #2b1a1a;
    color: #f87171;
    border-radius: 999px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 600;
}
QLabel#cardTitle {
    color: #ffffff;
    font-size: 13px;
    font-weight: 600;
}
QFrame#card {
    background: #121816;
    border: 1px solid #1f2a25;
    border-radius: 14px;
}
QLineEdit {
    background: #0d1210;
    border: 1px solid #243029;
    border-radius: 9px;
    padding: 9px 12px;
    color: #e6efe9;
    font-size: 13px;
    selection-background-color: #10b981;
}
QLineEdit:focus {
    border: 1px solid #10b981;
    background: #0e1512;
}
QPushButton {
    background: #141a17;
    color: #e6efe9;
    border: 1px solid #243029;
    border-radius: 9px;
    padding: 9px 16px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton:hover {
    background: #1b231f;
    border-color: #33413a;
}
QPushButton:pressed {
    background: #101512;
}
QPushButton#primary {
    background: #10b981;
    border: none;
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
    padding: 13px;
    border-radius: 11px;
}
QPushButton#primary:hover {
    background: #2fd39a;
}
QPushButton#primary:pressed {
    background: #0da271;
}
QPushButton#primary:disabled {
    background: #1c2420;
    color: #5f6f68;
}
QPlainTextEdit {
    background: #080c0a;
    border: 1px solid #1f2a25;
    border-radius: 10px;
    color: #6ee7b7;
    font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
    font-size: 12px;
    padding: 12px;
}
QMessageBox {
    background: #121816;
}
QMessageBox QLabel {
    color: #e6efe9;
    font-size: 13px;
}
QMessageBox QPushButton {
    background: #141a17;
    border: 1px solid #243029;
    border-radius: 8px;
    color: #e6efe9;
    padding: 8px 14px;
    font-weight: 600;
}
QMessageBox QPushButton:hover {
    background: #10b981;
    border-color: #10b981;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("USB Folder Sync")
        self.setMinimumSize(620, 560)

        central = QWidget()
        central.setObjectName("central")
        outer = QVBoxLayout(central)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(18)

        header = QHBoxLayout()
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        title = QLabel("USB Folder Sync")
        title.setObjectName("title")
        subtitle = QLabel("KeePass-style two-way sync between PC and phone over USB")
        subtitle.setObjectName("subtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        header.addLayout(title_block, 1)
        self.status = QLabel("●  No device checked")
        self.status.setObjectName("status")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(self.status)
        outer.addLayout(header)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(14)

        card_title = QLabel("Folders")
        card_title.setObjectName("cardTitle")
        card_layout.addWidget(card_title)

        pc_row = QHBoxLayout()
        pc_row.setSpacing(10)
        self.pc_edit = QLineEdit()
        self.pc_edit.setPlaceholderText("Choose the folder on this PC…")
        pc_button = QPushButton("Browse…")
        pc_button.clicked.connect(self.pick_pc)
        pc_row.addWidget(self.pc_edit, 1)
        pc_row.addWidget(pc_button)
        card_layout.addLayout(pc_row)

        phone_row = QHBoxLayout()
        phone_row.setSpacing(10)
        self.phone_edit = QLineEdit("/sdcard/Sync")
        self.phone_edit.setPlaceholderText("Folder on the phone, e.g. /sdcard/Sync")
        phone_row.addWidget(self.phone_edit, 1)
        card_layout.addLayout(phone_row)

        self.sync_button = QPushButton("Sync now")
        self.sync_button.setObjectName("primary")
        self.sync_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sync_button.clicked.connect(self.sync_now)
        card_layout.addWidget(self.sync_button)

        outer.addWidget(card)

        report_card = QFrame()
        report_card.setObjectName("card")
        report_layout = QVBoxLayout(report_card)
        report_layout.setContentsMargins(20, 16, 20, 16)
        report_layout.setSpacing(10)
        report_title = QLabel("Sync report")
        report_title.setObjectName("cardTitle")
        report_layout.addWidget(report_title)
        self.report = QPlainTextEdit()
        self.report.setReadOnly(True)
        self.report.setPlaceholderText("Nothing synced yet. Connect your phone and press “Sync now”.")
        report_layout.addWidget(self.report)
        outer.addWidget(report_card, 1)

        self.setCentralWidget(central)

    def set_status(self, text, kind="neutral"):
        self.status.setText(text)
        self.status.setObjectName({"ok": "statusOk", "warn": "statusWarn"}.get(kind, "status"))
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

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
        self.sync_button.setEnabled(False)
        self.set_status("●  Checking device and clocks…")
        try:
            ok, drift = engine.check_clocks()
        except adb.AdbError as exc:
            self.sync_button.setEnabled(True)
            self.set_status("●  No device", "warn")
            QMessageBox.critical(self, "USB error", str(exc))
            return
        if not ok:
            self.sync_button.setEnabled(True)
            self.set_status(f"●  Clocks off by {drift:.0f}s", "warn")
            QMessageBox.warning(
                self, "Clocks not synchronized",
                f"PC and phone clocks differ by {drift:.0f}s "
                f"(tolerance {engine.CLOCK_TOLERANCE_SECONDS}s). Sync aborted.")
            return
        self.set_status("●  Device connected · clocks in sync", "ok")
        try:
            report = engine.plan_sync(local_root, remote_root, self.decide)
            engine.execute(local_root, remote_root, report)
        except adb.AdbError as exc:
            self.sync_button.setEnabled(True)
            QMessageBox.critical(self, "Sync failed", str(exc))
            return
        self.sync_button.setEnabled(True)
        lines = [f"{item.action.upper():5}  {item.path}  —  {item.detail}" for item in report]
        self.report.setPlainText("\n".join(lines) if lines else "Nothing to do — both folders are already in sync.")


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
