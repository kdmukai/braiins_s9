# braiins_s9 python control
Programmatically start/stop mining on an S9 running Braiins OS.

If you issue a `stop` command via the API, mining will stop but the S9 fans will reset to MAX for some reason. So instead, this python code leverages the existing Braiins web UI to activate/deactivate the hashboards. This puts the S9 into a quieter idling state (fans still running, but at a minimal speed).

This approach is kind of ridiculous; we're using python to log into the web UI and submit the config html form.

But I haven't found a better approach.


## Installation
```
# linux:
sudo apt install chromium-chromedriver xvfb

# mac:
??? (sorry, didn't take great notes here)

# windows:
(didn't even try)
```

Install python dependencies:
```
pip install -r requirements.txt
```

## Sample usage
In some `main.py` that you create:
```
from braiins_s9 import BraiinsS9

try:
    s9 = BraiinsS9(ip_address="your.s9.ip.addr", username="foo", password="bar")

    # start mining
    if not s9.is_mining:
        s9.start_mining()

    # stop mining
    if s9.is_mining:
        s9.stop_mining()

finally:
    s9.quit()
```
