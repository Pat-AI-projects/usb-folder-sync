import os
import time
from dataclasses import dataclass

from . import adb

CLOCK_TOLERANCE_SECONDS = 60
MTIME_EPSILON_SECONDS = 1


@dataclass
class FileEntry:
    mtime: float
    size: int


@dataclass
class ReportItem:
    action: str
    path: str
    detail: str = ""


def check_clocks():
    phone = adb.device_time()
    pc = time.time()
    drift = abs(pc - phone)
    return drift <= CLOCK_TOLERANCE_SECONDS, drift


def scan_local(root):
    entries = {}
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            st = os.stat(full)
            entries[rel] = FileEntry(st.st_mtime, st.st_size)
    return entries


def _remote_path(remote_root, rel):
    return f"{remote_root.rstrip('/')}/{rel}"


def plan_sync(local_root, remote_root, decide):
    local = scan_local(local_root)
    remote = adb.list_files(remote_root)
    report = []
    for rel in sorted(set(local) | set(remote)):
        in_local = rel in local
        in_remote = rel in remote
        if in_local and in_remote:
            l, r = local[rel], remote[rel]
            if l.mtime > r.mtime + MTIME_EPSILON_SECONDS:
                report.append(ReportItem("push", rel, "newer on PC"))
            elif r.mtime > l.mtime + MTIME_EPSILON_SECONDS:
                report.append(ReportItem("pull", rel, "newer on phone"))
            elif l.size != r.size:
                choice = decide(rel, "same timestamp but different size")
                if choice == "pc":
                    report.append(ReportItem("push", rel, "resolved: PC version"))
                elif choice == "phone":
                    report.append(ReportItem("pull", rel, "resolved: phone version"))
                else:
                    report.append(ReportItem("skip", rel, "resolved: kept both"))
            else:
                report.append(ReportItem("skip", rel, "already in sync"))
        elif in_local:
            choice = decide(rel, "only on PC (new file, or deleted on phone?)")
            if choice == "copy":
                report.append(ReportItem("push", rel, "copied to phone"))
            else:
                report.append(ReportItem("skip", rel, "not copied"))
        else:
            choice = decide(rel, "only on phone (new file, or deleted on PC?)")
            if choice == "copy":
                report.append(ReportItem("pull", rel, "copied to PC"))
            else:
                report.append(ReportItem("skip", rel, "not copied"))
    return report


def execute(local_root, remote_root, report):
    for item in report:
        if item.action == "push":
            parent = os.path.dirname(_remote_path(remote_root, item.path))
            adb.makedirs(parent)
            adb.push(os.path.join(local_root, item.path), _remote_path(remote_root, item.path))
        elif item.action == "pull":
            local_path = os.path.join(local_root, item.path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            adb.pull(_remote_path(remote_root, item.path), local_path)
    return report
