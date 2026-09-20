# SamsungMXT40

This library communicates with Samsung MX-T40 devices through Bluetooth. It includes a command-line example and a Blueman plugin.

## Installation

Install the managed Python and uv versions:

```shell
mise install
```

Install the locked project dependencies:

```shell
mise run sync
```

Run the unit tests:

```shell
mise run test
```

## Get started

Use this code to connect to the device:

```Python
from samsungmxt40 import SamsungMXT40

samsung = SamsungMXT40("2C:FD:B3:E6:D1:08")

samsung.turn_off()
```

## main.py

This file contains a command-line example for the library features.

## SamsungMXT40Profile.py

This file contains a Blueman plugin. Create a symbolic link to this file in `$INSTALLATION_DIR/blueman/plugins/manager/`.
