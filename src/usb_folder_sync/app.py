import sys
import time
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QCheckBox, QFileDialog, QFrame,
                               QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                               QMainWindow, QMessageBox, QProgressBar,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)

from . import adb, engine

STYLESHEET = """
* {
    font-family: "Segoe UI", "Inter", "Helvetica Neue", sans-serif;
}
QMainWindow, QWidget#central, QWidget#mainArea {
    background: #0b0f0e;
}
QFrame#sidebar {
    background: #0e1311;
    border-right: 1px solid #1f2a25;
}
QLabel {
    color: #e6efe9;
    font-size: 13px;
}
QLabel#sideTitle {
    color: #ffffff;
    font-size: 15px;
    font-weight: 700;
}
QLabel#navActive {
    color: #34d399;
    background: #12241d;
    font-size: 13px;
    font-weight: 700;
    padding: 8px 12px;
    border-radius: 8px;
}
QLabel#title {
    color: #ffffff;
    font-size: 20px;
    font-weight: 700;
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
QLabel#kpiValue {
    color: #ffffff;
    font-size: 20px;
    font-weight: 700;
}
QLabel#kpiLabel {
    color: #8ba398;
    font-size: 11px;
    font-weight: 600;
}
QLabel#devLabel {
    color: #8ba398;
    font-size: 11px;
    font-weight: 600;
}
QLabel#devValue {
    color: #e6efe9;
    font-size: 12px;
}
QFrame#card {
    background: #121816;
    border: 1px solid #1f2a25;
    border-radius: 14px;
}
QFrame#devCard {
    background: #121816;
    border: 1px solid #1f2a25;
    border-radius: 12px;
}
QLineEdit {
    background: #0d1210;
    border: 1px solid #243029;
    border-radius: 9px;
    padding: 8px 12px;
    color: #e6efe9;
    font-size: 13px;
    selection-background-color: #10b981;
}
QLineEdit:focus {
    border: 1px solid #10b981;
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
    font-size: 13px;
    font-weight: 700;
    padding: 10px 18px;
    border-radius: 10px;
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
QPushButton#apply {
    background: #12241d;
    border: 1px solid #1f4636;
    color: #34d399;
    font-weight: 700;
    padding: 10px 18px;
    border-radius: 10px;
}
QPushButton#apply:hover {
    background: #173327;
}
QPushButton#apply:disabled {
    background: #1c2420;
    color: #5f6f68;
    border-color: #243029;
}
QTableWidget {
    background: #0d1210;
    border: 1px solid #1f2a25;
    border-radius: 10px;
    gridline-color: #1a231f;
    color: #e6efe9;
    font-size: 12px;
    selection-background-color: #12352a;
    outline: none;
}
QTableWidget::item {
    padding: 4px;
    border: none;
}
QHeaderView::section {
    background: #121816;
    color: #8ba398;
    border: none;
    border-bottom: 1px solid #1f2a25;
    padding: 9px 10px;
    font-size: 11px;
    font-weight: 700;
}
QCheckBox {
    color: #e6efe9;
    font-size: 12px;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #33413a;
    background: #0d1210;
}
QCheckBox::indicator:checked {
    background: #10b981;
    border-color: #10b981;
}
QProgressBar {
    background: #0d1210;
    border: none;
    border-radius: 6px;
    height: 10px;
    text-align: center;
}
QProgressBar::chunk {
    background: #10b981;
    border-radius: 6px;
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


def human_size(n):
    value = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{n} B"


def fmt_time(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else "—"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("USB Folder Sync")
        self.setMinimumSize(980, 640)
        self.plan = []

        central = QWidget()
        central.setObjectName("central")
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(16, 20, 16, 20)
        side_layout.setSpacing(14)

        side_title = QLabel("USB Folder Sync")
        side_title.setObjectName("sideTitle")
        side_layout.addWidget(side_title)

        nav_active = QLabel("⇄  Sync")
        nav_active.setObjectName("navActive")
        side_layout.addWidget(nav_active)
        side_layout.addSpacing(10)

        dev_card = QFrame()
        dev_card.setObjectName("devCard")
        dev_layout = QVBoxLayout(dev_card)
        dev_layout.setContentsMargins(14, 12, 14, 12)
        dev_layout.setSpacing(6)
        dev_header = QLabel("DEVICE")
        dev_header.setObjectName("devLabel")
        dev_layout.addWidget(dev_header)
        self.dev_model = QLabel("No device")
        self.dev_model.setObjectName("devValue")
        dev_layout.addWidget(self.dev_model)
        self.dev_drift = QLabel("drift: —")
        self.dev_drift.setObjectName("devValue")
        dev_layout.addWidget(self.dev_drift)
        self.dev_storage = QLabel("storage: —")
        self.dev_storage.setObjectName("devValue")
        dev_layout.addWidget(self.dev_storage)
        side_layout.addWidget(dev_card)
        side_layout.addStretch(1)

        root.addWidget(sidebar)

        main_area = QWidget()
        main_area.setObjectName("mainArea")
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Sync")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch(1)
        self.status = QLabel("●  No device checked")
        self.status.setObjectName("status")
        header.addWidget(self.status)
        main_layout.addLayout(header)

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)
        self.kpis = {}
        for key, label in (("files", "FILES IN PLAN"), ("size", "DATA TO MOVE"),
                           ("last", "LAST SYNC"), ("conflicts", "CONFLICTS")):
            card = QFrame()
            card.setObjectName("card")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            cl.setSpacing(2)
            value = QLabel("—")
            value.setObjectName("kpiValue")
            lab = QLabel(label)
            lab.setObjectName("kpiLabel")
            cl.addWidget(value)
            cl.addWidget(lab)
            kpi_row.addWidget(card)
            self.kpis[key] = value
        main_layout.addLayout(kpi_row)

        plan_card = QFrame()
        plan_card.setObjectName("card")
        plan_layout = QVBoxLayout(plan_card)
        plan_layout.setContentsMargins(18, 16, 18, 16)
        plan_layout.setSpacing(12)

        toolbar = QHBoxLayout()
        self.pc_edit = QLineEdit()
        self.pc_edit.setPlaceholderText("PC folder…")
        browse = QPushButton("Browse…")
        browse.clicked.connect(self.pick_pc)
        self.phone_edit = QLineEdit("/sdcard/Sync")
        self.phone_edit.setPlaceholderText("Phone folder, e.g. /sdcard/Sync")
        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter files…")
        self.search.setMaximumWidth(200)
        self.search.textChanged.connect(self.filter_table)
        self.select_all = QCheckBox("Select all")
        self.select_all.setChecked(True)
        self.select_all.stateChanged.connect(self.toggle_all)
        self.sync_button = QPushButton("Sync now")
        self.sync_button.setObjectName("primary")
        self.sync_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sync_button.clicked.connect(self.build_plan)
        self.apply_button = QPushButton("Apply selected")
        self.apply_button.setObjectName("apply")
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.apply_selected)
        toolbar.addWidget(self.pc_edit, 1)
        toolbar.addWidget(browse)
        toolbar.addWidget(self.phone_edit, 1)
        toolbar.addWidget(self.search)
        toolbar.addWidget(self.select_all)
        toolbar.addWidget(self.sync_button)
        toolbar.addWidget(self.apply_button)
        plan_layout.addLayout(toolbar)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["", "Action", "File", "Size", "Modified", "Reason"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table_header = self.table.horizontalHeader()
        table_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        table_header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        table_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table_header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        plan_layout.addWidget(self.table)

        progress_row = QHBoxLayout()
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress_label = QLabel("Idle")
        self.progress_label.setObjectName("devLabel")
        progress_row.addWidget(self.progress, 1)
        progress_row.addWidget(self.progress_label)
        plan_layout.addLayout(progress_row)

        main_layout.addWidget(plan_card, 1)
        root.addWidget(main_area, 1)
        self.setCentralWidget(central)

        self.refresh_device()

    def set_status(self, text, kind="neutral"):
        self.status.setText(text)
        self.status.setObjectName({"ok": "statusOk", "warn": "statusWarn"}.get(kind, "status"))
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

    def refresh_device(self):
        try:
            model = adb.device_model()
            ok, drift = engine.check_clocks()
            self.dev_model.setText(model)
            self.dev_drift.setText(f"clock drift: {drift:.0f}s / {engine.CLOCK_TOLERANCE_SECONDS}s tolerance")
            if ok:
                self.set_status(f"●  {model} · clocks in sync", "ok")
            else:
                self.set_status(f"●  {model} · clocks off by {drift:.0f}s", "warn")
            try:
                s = adb.storage(self.phone_edit.text().strip() or "/sdcard")
                self.dev_storage.setText(f"storage: {s['used']} used · {s['free']} free of {s['size']}")
            except adb.AdbError:
                self.dev_storage.setText("storage: —")
        except adb.AdbError:
            self.dev_model.setText("No device")
            self.dev_drift.setText("clock drift: —")
            self.dev_storage.setText("storage: —")
            self.set_status("●  No device", "warn")

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

    def build_plan(self):
        local_root = self.pc_edit.text().strip()
        remote_root = self.phone_edit.text().strip()
        if not local_root or not remote_root:
            QMessageBox.warning(self, "Missing folder", "Choose both the PC folder and the phone folder.")
            return
        self.sync_button.setEnabled(False)
        self.apply_button.setEnabled(False)
        self.set_status("●  Checking clocks…")
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
            engine.log_run(local_root, remote_root, [], False, drift)
            QMessageBox.warning(
                self, "Clocks not synchronized",
                f"PC and phone clocks differ by {drift:.0f}s "
                f"(tolerance {engine.CLOCK_TOLERANCE_SECONDS}s). Sync aborted.")
            return
        self.set_status("●  Device connected · clocks in sync", "ok")
        try:
            self.plan = engine.plan_sync(local_root, remote_root, self.decide)
        except adb.AdbError as exc:
            self.sync_button.setEnabled(True)
            QMessageBox.critical(self, "Plan failed", str(exc))
            return
        self.sync_button.setEnabled(True)
        self.fill_table(self.plan)
        self.apply_button.setEnabled(True)
        moved = sum(i.size for i in self.plan if i.action in ("push", "pull"))
        conflicts = sum(1 for i in self.plan if "resolved" in i.detail)
        self.kpis["files"].setText(str(len(self.plan)))
        self.kpis["size"].setText(human_size(moved))
        self.kpis["conflicts"].setText(str(conflicts))
        self.progress.setValue(0)
        self.progress_label.setText(f"Plan ready: {len(self.plan)} files")

    def fill_table(self, items):
        self.table.setRowCount(0)
        for row, item in enumerate(items):
            self.table.insertRow(row)
            check = QTableWidgetItem()
            check.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            check.setCheckState(Qt.CheckState.Checked if item.action != "skip" else Qt.CheckState.Unchecked)
            self.table.setItem(row, 0, check)
            self.table.setItem(row, 1, QTableWidgetItem(item.action.upper()))
            self.table.setItem(row, 2, QTableWidgetItem(item.path))
            self.table.setItem(row, 3, QTableWidgetItem(human_size(item.size)))
            self.table.setItem(row, 4, QTableWidgetItem(fmt_time(item.mtime)))
            self.table.setItem(row, 5, QTableWidgetItem(item.detail))
        self.filter_table(self.search.text())

    def filter_table(self, text):
        needle = text.strip().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 2)
            self.table.setRowHidden(row, bool(needle) and needle not in (item.text().lower() if item else ""))

    def toggle_all(self, state):
        checked = state == Qt.CheckState.Checked.value
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

    def selected_items(self):
        items = []
        for row in range(self.table.rowCount()):
            check = self.table.item(row, 0)
            if check and check.checkState() == Qt.CheckState.Checked:
                items.append(self.plan[row])
        return items

    def on_progress(self, path, frac):
        self.progress.setValue(int(frac * 100))
        self.progress_label.setText(path if path else "Done")

    def apply_selected(self):
        local_root = self.pc_edit.text().strip()
        remote_root = self.phone_edit.text().strip()
        items = [i for i in self.selected_items() if i.action in ("push", "pull")]
        self.apply_button.setEnabled(False)
        self.sync_button.setEnabled(False)
        try:
            engine.apply(local_root, remote_root, items, progress=self.on_progress)
            engine.log_run(local_root, remote_root, self.plan, True, 0)
        except adb.AdbError as exc:
            QMessageBox.critical(self, "Sync failed", str(exc))
        self.sync_button.setEnabled(True)
        self.apply_button.setEnabled(True)
        self.kpis["last"].setText(datetime.now().strftime("%H:%M"))
        self.progress_label.setText(f"Applied {len(items)} file(s)")
        self.set_status("●  Sync complete", "ok")


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
