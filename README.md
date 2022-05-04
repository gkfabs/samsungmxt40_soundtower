# SamsungMXT40
A library to communicate on bluetooth with Samsung MX-T40 devices with command line example and blueman plugin

### Installation

### Get started
How to connect to the device:

```Python
from samsungmxt40 import SamsungMXT40

# Connection
samsung = SamsungMXT40("2C:FD:B3:E6:D1:08")

# Call the turn_off method
samsung.turn_off()
```

### main.py
that's an exaustive command line example of what's capable the lib

### SamsungMXT40Profile.py
that's a plugin for blueman

You need to create a symbolic link of this file in $INSTALLATION_DIR/blueman/plugins/manager/
