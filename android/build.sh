#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
TOOLS="${ANDROID_BUILD_TOOLS:-/workspace/android-tools/build/android-15}"
PLATFORM="${ANDROID_JAR:-/workspace/android-tools/platform/android-35/android.jar}"
OUT="$PWD/build"
mkdir -p "$OUT/classes" "$OUT/dex" "$OUT/assets/game"
cp -R ../megabrain/. "$OUT/assets/game/"
# Use local system fonts: the APK never needs network access.
python3 - "$OUT/assets/game/style.css" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]);p.write_text('\n'.join(line for line in p.read_text().splitlines() if not line.startswith('@import ')))
PY
"$TOOLS/aapt2" compile --dir res -o "$OUT/resources.zip"
"$TOOLS/aapt2" link -o "$OUT/base.apk" -I "$PLATFORM" --manifest AndroidManifest.xml -A "$OUT/assets" "$OUT/resources.zip"
java -jar "${ECJ_JAR:-/workspace/android-tools/ecj.jar}" -encoding UTF-8 -8 -classpath "$PLATFORM" -d "$OUT/classes" src/com/megabrain/bobsnake/MainActivity.java
find "$OUT/classes" -name '*.class' -print0 | xargs -0 "$TOOLS/d8" --lib "$PLATFORM" --min-api 23 --output "$OUT/dex"
cp "$OUT/base.apk" "$OUT/unsigned.apk"
(cd "$OUT/dex" && zip -q -u "$OUT/unsigned.apk" classes.dex)
"$TOOLS/zipalign" -f -p 4 "$OUT/unsigned.apk" "$OUT/aligned.apk"
# Keep this private key outside version control; reuse it for future updates.
KEYSTORE="${BOB_SNAKE_KEYSTORE:-/workspace/android-signing/bob-snake.jks}"
mkdir -p "$(dirname "$KEYSTORE")"
if [[ ! -f "$KEYSTORE" ]]; then
    keytool -genkeypair -keystore "$KEYSTORE" -alias bobsnake -keyalg RSA -keysize 3072 -validity 10000 -storepass android -keypass android -dname 'CN=Bob Snake Local, O=Megabrain, C=BR' </dev/null
    chmod 600 "$KEYSTORE"
fi
"$TOOLS/apksigner" sign --ks "$KEYSTORE" --ks-key-alias bobsnake --ks-pass pass:android --key-pass pass:android --out "$OUT/Bob-Esponja-Snake.apk" "$OUT/aligned.apk"
"$TOOLS/apksigner" verify --verbose "$OUT/Bob-Esponja-Snake.apk"
"$TOOLS/zipalign" -c -v 4 "$OUT/Bob-Esponja-Snake.apk"
