# usb-folder-sync

A Windows desktop app that synchronizes a folder tree on your PC with a
folder tree on your Android phone connected by USB cable. Like KeePass sync, it
keeps only the most recently modified version of each file — and before syncing,
it verifies that both devices' clocks are synchronized.

## Features
- Sidebar with a live **device card**: phone model, clock drift vs tolerance,
  and phone storage usage.
- **KPI cards**: files in plan, data to move, last sync time, conflicts.
- **Dry-run plan table**: "Sync now" builds the full plan first; review it,
  filter with the search box, untick files, then **Apply selected**.
- **Progress bar** with the current file during transfer.
- Every run is appended to `~/.usb_folder_sync/history.json`.
- Emerald Night premium dark theme (PySide6 stylesheet).

## Requirements

### Devices and transport
- **Computer:** Windows PC.
- **Phone:** Android, connected to the PC with a wired USB link.
- Phone storage is accessed over USB via `adb` (requires enabling USB
  debugging once on the phone, in Developer options). No cloud service and
  no network sync are involved.

### Trigger and UI
- Manual, on demand: pick the PC folder (Browse…) and the phone folder
  (e.g. `/sdcard/Sync`), press **Sync now** to preview the plan, then
  **Apply selected** to execute it.

### Scope
- **Entire folder trees are mirrored bidirectionally** (PC → phone and
  phone → PC). Content is mixed: any file types must be supported.

### Conflict resolution (KeePass-style, last-write-wins)
- When the same file exists on both sides with different content, the version
  with the **newest modification timestamp wins** and overwrites the other.
- For **deletions** and any ambiguous conflict, the app **asks the user each
  time** what to do. It never silently deletes or overwrites without consent.

### Time synchronization check
- Before any sync, the app compares the PC's clock with the phone's clock
  (read over the USB link). If they differ by **more than 1 minute**, the app
  **shows a warning and aborts the sync**, because wrong timestamps would
  cause incorrect last-write-wins decisions.

### Safety
- No destructive or ambiguous action happens without explicit user
  confirmation.

## Project structure
- `src/usb_folder_sync/app.py` — PySide6 window: sidebar + device card, KPI
  cards, plan table, progress bar, decision dialogs.
- `src/usb_folder_sync/adb.py` — thin wrapper around the `adb` CLI: device
  check, model, clock, storage, remote file listing with mtimes, pull/push.
- `src/usb_folder_sync/engine.py` — clock check, local/remote tree scan,
  last-write-wins planning, apply with progress, run history.

## Running
1. Install Android platform-tools (provides `adb`) and add it to `PATH`.
2. On the phone, enable Developer options → USB debugging.
3. `pip install -r requirements.txt`
4. Run with `src` on `PYTHONPATH`: `python -m usb_folder_sync`, plug in the
   phone, choose both folders, click "Sync now", review the plan, then
   "Apply selected".

## Acceptance criteria
1. Plugging in the phone and applying the plan mirrors both folder trees.
2. For a file changed on both sides, the newest version ends up on both sides.
3. Deletions and conflicts always prompt the user; nothing is deleted silently.
4. If the PC and phone clocks differ by more than 1 minute, the sync warns and aborts.
5. The plan table lists every file with its action, size, mtime and reason.

## License
[MIT](LICENSE)
