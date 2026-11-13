import os
import sys
import time
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
                               QFileDialog, QFrame, QHBoxLayout, QHeaderView,
                               QLabel, QLineEdit, QListWidget, QMainWindow,
                               QMessageBox, QProgressBar, QPushButton,
                               QTableWidget, QTableWidgetItem, QVBoxLayout,
                               QWidget)

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
QLabel#navItem {
    color: #8ba398;
    font-size: 13px;
    font-weight: 600;
    padding: 8px 12px;
    border-radius: 8px;
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
QLabel#cardTitle {
    color: #ffffff;
    font-size: 13px;
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
    padding: 10px 13px;
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
    padding: 10px 18px;
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
    padding: 6px;
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
    image: url(__CHECK__);
}
QTableWidget::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #33413a;
    background: #0d1210;
}
QTableWidget::indicator:checked {
    background: #10b981;
    border-color: #10b981;
    image: url(__CHECK__);
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
QListWidget {
    background: #0d1210;
    border: 1px solid #243029;
    border-radius: 10px;
    color: #e6efe9;
    font-size: 13px;
    padding: 6px;
    outline: none;
}
QListWidget::item {
    padding: 7px 10px;
    border-radius: 6px;
}
QListWidget::item:hover {
    background: #16211c;
}
QListWidget::item:selected {
    background: #12352a;
    color: #34d399;
}
QDialog {
    background: #0e1311;
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

LIGHT_STYLESHEET = """
* {
    font-family: "Segoe UI", "Inter", "Helvetica Neue", sans-serif;
}
QMainWindow, QWidget#central, QWidget#mainArea {
    background: #f7f8fa;
}
QFrame#sidebar {
    background: #ffffff;
    border-right: 1px solid #e5e7eb;
}
QLabel {
    color: #1f2937;
    font-size: 13px;
}
QLabel#sideTitle {
    color: #111827;
    font-size: 15px;
    font-weight: 700;
}
QLabel#navActive {
    color: #059669;
    background: #ecfdf5;
    font-size: 13px;
    font-weight: 700;
    padding: 8px 12px;
    border-radius: 8px;
}
QLabel#title {
    color: #111827;
    font-size: 20px;
    font-weight: 700;
}
QLabel#status {
    background: #eef0f3;
    color: #6b7280;
    border-radius: 999px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 600;
}
QLabel#statusOk {
    background: #ecfdf5;
    color: #059669;
    border-radius: 999px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 600;
}
QLabel#statusWarn {
    background: #fef2f2;
    color: #dc2626;
    border-radius: 999px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 600;
}
QLabel#kpiValue {
    color: #111827;
    font-size: 20px;
    font-weight: 700;
}
QLabel#kpiLabel {
    color: #6b7280;
    font-size: 11px;
    font-weight: 600;
}
QLabel#devLabel {
    color: #6b7280;
    font-size: 11px;
    font-weight: 600;
}
QLabel#devValue {
    color: #1f2937;
    font-size: 12px;
}
QFrame#card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
}
QFrame#devCard {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
}
QLineEdit {
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 9px;
    padding: 10px 13px;
    color: #111827;
    font-size: 13px;
    selection-background-color: #a7f3d0;
}
QLineEdit:focus {
    border: 1px solid #10b981;
}
QPushButton {
    background: #ffffff;
    color: #1f2937;
    border: 1px solid #d1d5db;
    border-radius: 9px;
    padding: 10px 18px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton:hover {
    background: #f3f4f6;
    border-color: #9ca3af;
}
QPushButton:pressed {
    background: #e5e7eb;
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
    background: #34d399;
}
QPushButton#primary:pressed {
    background: #059669;
}
QPushButton#primary:disabled {
    background: #e5e7eb;
    color: #9ca3af;
}
QPushButton#apply {
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    color: #059669;
    font-weight: 700;
    padding: 10px 18px;
    border-radius: 10px;
}
QPushButton#apply:hover {
    background: #d1fae5;
}
QPushButton#apply:disabled {
    background: #e5e7eb;
    color: #9ca3af;
    border-color: #d1d5db;
}
QTableWidget {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    gridline-color: #eef0f3;
    color: #1f2937;
    font-size: 12px;
    selection-background-color: #d1fae5;
    outline: none;
}
QTableWidget::item {
    padding: 6px;
    border: none;
}
QHeaderView::section {
    background: #f9fafb;
    color: #6b7280;
    border: none;
    border-bottom: 1px solid #e5e7eb;
    padding: 9px 10px;
    font-size: 11px;
    font-weight: 700;
}
QCheckBox {
    color: #1f2937;
    font-size: 12px;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #d1d5db;
    background: #ffffff;
}
QCheckBox::indicator:checked {
    background: #10b981;
    border-color: #10b981;
    image: url(__CHECK__);
}
QTableWidget::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #d1d5db;
    background: #ffffff;
}
QTableWidget::indicator:checked {
    background: #10b981;
    border-color: #10b981;
    image: url(__CHECK__);
}
QProgressBar {
    background: #eef0f3;
    border: none;
    border-radius: 6px;
    height: 10px;
    text-align: center;
}
QProgressBar::chunk {
    background: #10b981;
    border-radius: 6px;
}
QListWidget {
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    color: #1f2937;
    font-size: 13px;
    padding: 6px;
    outline: none;
}
QListWidget::item {
    padding: 7px 10px;
    border-radius: 6px;
}
QListWidget::item:hover {
    background: #f3f4f6;
}
QListWidget::item:selected {
    background: #d1fae5;
    color: #065f46;
}
QDialog {
    background: #ffffff;
}
QMessageBox {
    background: #ffffff;
}
QMessageBox QLabel {
    color: #1f2937;
    font-size: 13px;
}
QMessageBox QPushButton {
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    color: #1f2937;
    padding: 8px 14px;
    font-weight: 600;
}
QMessageBox QPushButton:hover {
    background: #10b981;
    border-color: #10b981;
    color: #ffffff;
}
"""

THEMES = {"dark": STYLESHEET, "light": LIGHT_STYLESHEET}


def _check_icon_path():
    from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
    path = os.path.join(os.path.dirname(engine.CONFIG_PATH), "check.png")
    if not os.path.exists(path):
        pix = QPixmap(32, 32)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#ffffff"))
        pen.setWidth(4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(8, 17, 14, 23)
        painter.drawLine(14, 23, 25, 9)
        painter.end()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        pix.save(path)
    return path


def themed_stylesheet(theme):
    return THEMES[theme].replace("__CHECK__", _check_icon_path())


ACTION_COLORS = {"push": "#34d399", "pull": "#22d3ee", "skip": "#8ba398"}


def human_size(n):
    value = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{n} B"


def fmt_time(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else "—"


FILTER_KINDS = [("name", "file name contains"), ("extension", "extension"), ("path", "path contains")]


def matches_filters(path, filters):
    name = path.rsplit("/", 1)[-1].lower()
    for f in filters:
        v = f["value"].lower()
        if f["kind"] == "name" and v not in name:
            return False
        if f["kind"] == "extension":
            ext = v if v.startswith(".") else "." + v
            if not name.endswith(ext):
                return False
        if f["kind"] == "path" and v not in path.lower():
            return False
    return True


class FilterDialog(QDialog):
    def __init__(self, parent, filters, sample_paths):
        super().__init__(parent)
        self.setWindowTitle("Filters")
        self.setMinimumSize(480, 400)
        self.filters = [dict(f) for f in filters]
        self.sample_paths = sample_paths
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        info = QLabel("Only files matching ALL filters are shown in the plan table. Double-click a filter to remove it.")
        info.setObjectName("devLabel")
        info.setWordWrap(True)
        layout.addWidget(info)
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.remove_filter)
        layout.addWidget(self.list)
        add_row = QHBoxLayout()
        self.kind = QComboBox()
        self.kind.addItems([label for _key, label in FILTER_KINDS])
        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("e.g. report   or   .jpg   or   /DCIM/")
        add_btn = QPushButton("Add filter")
        add_btn.clicked.connect(self.add_filter)
        add_row.addWidget(self.kind)
        add_row.addWidget(self.value_edit, 1)
        add_row.addWidget(add_btn)
        layout.addLayout(add_row)
        self.count_label = QLabel("")
        self.count_label.setObjectName("devValue")
        layout.addWidget(self.count_label)
        buttons = QHBoxLayout()
        clear = QPushButton("Clear all")
        clear.clicked.connect(self.clear_all)
        buttons.addWidget(clear)
        buttons.addStretch(1)
        ok = QPushButton("Apply")
        ok.setObjectName("primary")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(ok)
        buttons.addWidget(cancel)
        layout.addLayout(buttons)
        self.redraw()

    def add_filter(self):
        value = self.value_edit.text().strip()
        if not value:
            return
        kind = FILTER_KINDS[self.kind.currentIndex()][0]
        self.filters.append({"kind": kind, "value": value})
        self.value_edit.clear()
        self.redraw()

    def remove_filter(self, item):
        row = self.list.row(item)
        if 0 <= row < len(self.filters):
            self.filters.pop(row)
        self.redraw()

    def clear_all(self):
        self.filters = []
        self.redraw()

    def redraw(self):
        self.list.clear()
        labels = dict(FILTER_KINDS)
        for f in self.filters:
            self.list.addItem(f"{labels[f['kind']]}:  {f['value']}")
        if self.sample_paths:
            n = sum(1 for p in self.sample_paths if matches_filters(p, self.filters))
            self.count_label.setText(f"{n} of {len(self.sample_paths)} files in the current plan match")
        else:
            self.count_label.setText("Build a plan first to see live match counts")


class RemoteFolderDialog(QDialog):
    def __init__(self, parent, start):
        super().__init__(parent)
        self.setWindowTitle("Choose phone folder")
        self.setMinimumSize(420, 420)
        self.current = start.rstrip("/") or "/"
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        self.path_label = QLabel(self.current)
        self.path_label.setObjectName("devValue")
        layout.addWidget(self.path_label)
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.enter)
        layout.addWidget(self.list)
        buttons = QHBoxLayout()
        up = QPushButton("Up")
        up.clicked.connect(self.go_up)
        buttons.addWidget(up)
        buttons.addStretch(1)
        select = QPushButton("Select this folder")
        select.setObjectName("primary")
        select.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(select)
        buttons.addWidget(cancel)
        layout.addLayout(buttons)
        self.refresh()

    def refresh(self):
        self.path_label.setText(self.current)
        self.list.clear()
        try:
            dirs = adb.list_dirs(self.current)
        except adb.AdbError as exc:
            QMessageBox.critical(self, "USB error", str(exc))
            return
        for d in dirs:
            self.list.addItem(f"📁 {d}")

    def enter(self, item):
        self.current = f"{self.current.rstrip('/')}/{item.text().removeprefix('📁 ')}"
        self.refresh()

    def go_up(self):
        parent = self.current.rsplit("/", 1)[0] or "/"
        self.current = parent
        self.refresh()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("USB Folder Sync")
        self.setMinimumSize(880, 600)
        self.plan = []
        self.filters = []

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
        side_layout.addSpacing(6)
        self.theme_button = QPushButton()
        self.theme_button.clicked.connect(self.toggle_theme)
        side_layout.addWidget(self.theme_button)
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

        folders_row = QHBoxLayout()
        folders_row.setSpacing(10)
        self.pc_edit = QLineEdit()
        self.pc_edit.setPlaceholderText("PC folder…")
        browse = QPushButton("Browse…")
        browse.clicked.connect(self.pick_pc)
        self.phone_edit = QLineEdit("/sdcard/Sync")
        self.phone_edit.setPlaceholderText("Phone folder, e.g. /sdcard/Sync")
        phone_browse = QPushButton("Browse…")
        phone_browse.clicked.connect(self.pick_phone)
        folders_row.addWidget(self.pc_edit, 1)
        folders_row.addWidget(browse)
        folders_row.addWidget(self.phone_edit, 1)
        folders_row.addWidget(phone_browse)
        plan_layout.addLayout(folders_row)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Quick filter: type a file name…")
        self.search.textChanged.connect(self.filter_table)
        self.filters_button = QPushButton("Filters")
        self.filters_button.clicked.connect(self.open_filter_dialog)
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
        actions_row.addWidget(self.search, 1)
        actions_row.addWidget(self.filters_button)
        actions_row.addWidget(self.select_all)
        actions_row.addStretch(1)
        actions_row.addWidget(self.sync_button)
        actions_row.addWidget(self.apply_button)
        plan_layout.addLayout(actions_row)

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

        self.theme = engine.load_config().get("theme", "dark")
        self.update_theme_button()
        self.refresh_device()

    def update_theme_button(self):
        self.theme_button.setText("☀  Switch to light mode" if self.theme == "dark" else "🌙  Switch to dark mode")

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        QApplication.instance().setStyleSheet(themed_stylesheet(self.theme))
        cfg = engine.load_config()
        cfg["theme"] = self.theme
        engine.save_config(cfg)
        self.update_theme_button()
        self.set_status(self.status.text(), {"statusOk": "ok", "statusWarn": "warn"}.get(self.status.objectName(), "neutral"))

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

    def pick_phone(self):
        start = self.phone_edit.text().strip() or "/sdcard"
        dlg = RemoteFolderDialog(self, start)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.phone_edit.setText(dlg.current)
            self.refresh_device()

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

    def open_filter_dialog(self):
        dlg = FilterDialog(self, self.filters, [i.path for i in self.plan])
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.filters = dlg.filters
            self.filters_button.setText("Filters" if not self.filters else f"Filters ({len(self.filters)})")
            self.filter_table(self.search.text())

    def filter_table(self, text):
        needle = text.strip().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 2)
            path = item.text() if item else ""
            visible = (not needle or needle in path.lower()) and matches_filters(path, self.filters)
            self.table.setRowHidden(row, not visible)

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
    app.setStyleSheet(themed_stylesheet(engine.load_config().get("theme", "dark")))
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
