# usb-folder-sync

A small Windows desktop app that synchronizes a folder tree on your PC with a
folder tree on your Android phone connected by USB cable. Like KeePass sync, it
keeps only the most recently modified version of each file — and before syncing,
it verifies that both devices' clocks are synchronized.

## Requirements

### Devices and transport
- **Computer:** Windows PC.
- **Phone:** Android, connected to the PC with a wired USB link.
- Phone storage is accessed over USB via `adb` (requires enabling USB
  debugging once on the phone, in Developer options). No cloud service and
  no network sync are involved.

### Trigger and UI
- Synchronization runs **manually, on demand**: a desktop app (PySide6) with a
  **"Sync now"** button.
- Both folders are chosen each run: a folder picker for the PC folder and a
  text field for the phone folder (e.g. `/sdcard/Sync`).
- After a run, the app shows a **report of everything it did**: files copied in
  each direction, files skipped, and conflicts resolved.

### Scope
- **Entire folder trees are mirrored bidirectionally** (PC → phone and
  phone → PC).
- Content is mixed: any file types must be supported.

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
- `src/usb_folder_sync/app.py` — PySide6 window: folder pickers, "Sync now"
  button, report view, decision dialogs.
- `src/usb_folder_sync/adb.py` — thin wrapper around the `adb` CLI: device
  check, phone clock, remote file listing with mtimes, `pull`/`push`.
- `src/usb_folder_sync/engine.py` — clock check, local/remote tree scan,
  last-write-wins planning, conflict decisions, execution.

## Running
1. Install Android platform-tools (provides `adb`) and add it to `PATH`.
2. On the phone, enable Developer options → USB debugging.
3. `pip install -r requirements.txt`
4. Run with `src` on `PYTHONPATH`: `python -m usb_folder_sync`, plug in the
   phone, choose both folders, click "Sync now".

## Acceptance criteria
1. Plugging in the phone and clicking "Sync now" mirrors both folder trees.
2. For a file changed on both sides, the newest version ends up on both sides.
3. Deletions and conflicts always prompt the user; nothing is deleted silently.
4. If the PC and phone clocks differ by more than 1 minute, the sync warns and aborts.
5. A run report lists every copied, skipped, and resolved file.

## License
[MIT](LICENSE)
