#!/usr/bin/env python3
"""Download pinned build tools with upstream integrity checks; needs Java 21 runtime."""
import hashlib
import os
from pathlib import Path
import urllib.request
import zipfile

root = Path(os.environ.get('BOB_ANDROID_TOOLS', '/workspace/android-tools'))
root.mkdir(parents=True, exist_ok=True)
artifacts = [
    ('https://dl.google.com/android/repository/build-tools_r35_linux.zip', '2cfaa0bbb2336e9ec18ed3ecea84fa2e2af607bc', 'build'),
    ('https://dl.google.com/android/repository/platform-35_r02.zip', '0bb560a90a7a2cbd0dd8348224d518b638fe7949', 'platform'),
    ('https://repo.maven.apache.org/maven2/org/eclipse/jdt/ecj/3.40.0/ecj-3.40.0.jar', None, None),
]
for url, expected, directory in artifacts:
    data = urllib.request.urlopen(url, timeout=120).read()
    if expected is None:
        expected = urllib.request.urlopen(url + '.sha1', timeout=30).read().decode().strip()
    if hashlib.sha1(data).hexdigest() != expected:
        raise RuntimeError('Checksum mismatch: ' + url)
    target = root / ('ecj.jar' if directory is None else url.rsplit('/', 1)[1])
    target.write_bytes(data)
    if directory:
        with zipfile.ZipFile(target) as archive:
            archive.extractall(root / directory)
    print('Verified:', target.name)
for name in ('aapt2', 'd8', 'zipalign', 'apksigner'):
    (root / 'build/android-15' / name).chmod(0o755)
