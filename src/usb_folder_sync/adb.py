import shlex
import shutil
import subprocess


class AdbError(RuntimeError):
    pass


def find_adb():
    adb = shutil.which("adb")
    if adb:
        return adb
    raise AdbError("adb executable not found. Install Android platform-tools and add adb to PATH.")


def _run(args, binary=False):
    proc = subprocess.run([find_adb(), *args], capture_output=True)
    if proc.returncode != 0:
        raise AdbError(proc.stderr.decode(errors="replace").strip())
    if binary:
        return proc.stdout
    return proc.stdout.decode(errors="replace")


def _remote(cmd):
    return _run(["shell", cmd])


def ensure_device():
    out = _run(["devices"])
    states = [line.split("\t")[1] for line in out.splitlines()[1:] if "\t" in line]
    if "device" not in states:
        raise AdbError("No Android device connected over USB.")


def device_time():
    ensure_device()
    return int(_remote("date +%s").strip())


def list_files(remote_dir):
    cmd = f"find {shlex.quote(remote_dir)} -type f -exec stat -c '%Y|%s|%n' {{}} +"
    out = _remote(cmd)
    files = {}
    prefix = remote_dir.rstrip("/") + "/"
    for line in out.splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        mtime, size, path = line.split("|", 2)
        rel = path[len(prefix):] if path.startswith(prefix) else path
        files[rel] = (float(mtime), int(size))
    return files


def makedirs(remote_dir):
    _remote(f"mkdir -p {shlex.quote(remote_dir)}")


def pull(remote_path, local_path):
    _run(["pull", remote_path, local_path])


def push(local_path, remote_path):
    _run(["push", local_path, remote_path])
