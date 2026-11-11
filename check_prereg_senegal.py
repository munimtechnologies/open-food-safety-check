# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
# Waits (up to 60 minutes) until the senegal-groundnut 0.1.0 pre-registration is public on GitHub, so no data
# value is read before the plan is committed. Then downloads the published files of the same repository into
# the current folder (the code that runs is the code that was published):
#   python check_prereg_senegal.py [paths ...]
# Exits 1 if anything is missing.
import sys
import time
import urllib.error
import urllib.request

RAW = "https://raw.githubusercontent.com/munimtechnologies/open-food-safety-check/main/"
URL = RAW + "docs/senegal-groundnut-0.1.0.md"
MARKER = "PREREG-MARKER: senegal-groundnut-0.1.0"


def get(url):
    with urllib.request.urlopen(url, timeout=60) as resp:
        return resp.read()


for attempt in range(61):
    try:
        text = get(URL).decode("utf-8", "replace")
        if MARKER in text:
            print("pre-registration is public:", URL, len(text), "chars, attempt", attempt, flush=True)
            break
        print("attempt", attempt, "marker not found yet", flush=True)
    except (urllib.error.URLError, OSError) as exc:
        print("attempt", attempt, "not yet:", exc, flush=True)
    time.sleep(60)
else:
    print("pre-registration never appeared at", URL, flush=True)
    sys.exit(1)

for path in sys.argv[1:]:
    data = get(RAW + path)
    name = path.rsplit("/", 1)[-1]
    with open(name, "wb") as fh:
        fh.write(data)
    print("fetched", path, len(data), "bytes ->", name, flush=True)
