# usb-folder-sync

A small Windows desktop app that synchronizes a folder tree on your PC with a
folder tree on your Android phone connected by USB cable. Like KeePass sync, it
keeps only the most recently modified version of each file — and before syncing,
it verifies that both devices' clocks are synchronized.

## Requirements

### Devices and transport
- **Computer:** Windows PC.
- **Phone:** Android, connected to the PC with a wired USB link.
- Phone storage is accessed over MTP (USB). No cloud service and no network
  sync are involved.

### Trigger and UI
- Synchronization runs **manually, on demand**: a desktop app with a
  **"Sync now"** button.
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
- Before any sync, the app compares the PC's clock with the phone's clock.
- If the two clocks differ beyond a small tolerance, the app **shows a warning
  and aborts the sync**, because wrong timestamps would cause incorrect
  last-write-wins decisions.

### Safety
- No destructive or ambiguous action happens without explicit user
  confirmation.

## Suggested approach
- Windows desktop app (e.g. Python with a simple GUI toolkit) with a single
  "Sync now" button.
- Read the phone's file tree and modification times over MTP/USB.
- Walk both trees, compare modification timestamps, and copy the newer version
  in each direction.
- Prompt interactively for deletions and conflicts; log every action for the
  final report.

## Acceptance criteria
1. Plugging in the phone and clicking "Sync now" mirrors both folder trees.
2. For a file changed on both sides, the newest version ends up on both sides.
3. Deletions and conflicts always prompt the user; nothing is deleted silently.
4. If the PC and phone clocks disagree, the sync warns and aborts.
5. A run report lists every copied, skipped, and resolved file.

## License
[MIT](LICENSE)
