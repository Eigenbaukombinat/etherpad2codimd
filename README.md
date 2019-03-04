# Script to migrate a pad from etherpad to codimd, preserving its speaking name in the URL.

:::warn
This is currently untested as we have not yet installed our codimd instance.
:::

## Installation

```
git clone https://github.com/Eigenbaukombinat/etherpad2codimd.git
cd etherpad2codimd
python3 -m venv .
bin/pip install -r requirements.txt
```

## Configuration

```
copy config.py.example config.py
```

Then, edit config.py to your needs.
Please note that you must allow "free urls" in your codimd. (`CMD_ALLOW_FREEURL`)

## Usage

```
bin/python migrate.py <padname>
```

Will add a new pad <padname> in your codimd, and transfer the contents from the old etherpad into it. Note that if the pad already exists in codimd its content will be overwritten without a warning!

