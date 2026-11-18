import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time

parser = argparse.ArgumentParser(description='Verify a 256 MiB write and read on a Linux filesystem.')
parser.add_argument('--directory', type=Path, default=Path('/var/tmp'),
                    help='Existing writable directory on the filesystem to test (default: /var/tmp)')
directory = parser.parse_args().directory.resolve()
try:
    fd, name = tempfile.mkstemp(prefix='nais-storage-check-', dir=directory)
except OSError as error:
    parser.exit(1, f'Cannot create the storage test file in {directory}: {error}\n')
path = Path(name)
try:
    expected = hashlib.sha256()
    started = time.monotonic()
    with os.fdopen(fd, 'w+b', buffering=0) as disk_file:
        for _ in range(256):
            data = os.urandom(1024 * 1024)
            expected.update(data)
            if disk_file.write(data) != len(data):
                raise RuntimeError('Short test write')
        os.fsync(disk_file.fileno())
        write_seconds = time.monotonic() - started
        os.posix_fadvise(disk_file.fileno(), 0, 0, os.POSIX_FADV_DONTNEED)
        disk_file.seek(0)
        started = time.monotonic()
        actual = hashlib.file_digest(disk_file, 'sha256').hexdigest()
        read_seconds = time.monotonic() - started
    if actual != expected.hexdigest():
        raise RuntimeError('SSD test read-back checksum mismatch')
    print(json.dumps({'verified': True, 'directory': str(directory), 'bytes': 256*1024*1024, 'write_and_fsync_seconds': round(write_seconds, 2), 'read_and_hash_seconds': round(read_seconds, 2), 'sha256': actual}))
finally:
    path.unlink(missing_ok=True)
