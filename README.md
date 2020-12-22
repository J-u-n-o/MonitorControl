# MonitorControl
Control and have synced your monitor brightness and contrast controls

A (small) python utility for windows 10 detecting your attached internal/laptop and external monitors, and to control and sync their brightness and contrasts. 
This requires an external monitor having DDC/CI support and have this enabled.

It is a tray application, and a window will popup when clicked.
When running it syncs the values as set by the windows system (brightness) slider, the laptop (keyboard) brightness control, and using the contrast and brightness controls of your monitor.
Also it has sliders to control the contrast and brightness by your mouse for all monitors.
To prevent brightness differences there is a per monitor calibration for brightness and contrast in the setup tab of the window. This to make sure e.g. 50% brightness is equal for all monitors.


Note:
Not all monitors support changing contrast, at least access was not present for my laptop monitor.
It requires an external monitor having DDC/CI support and have this enabled.
It detects windows being restored from sleep/hibernation, though some/at lot of rough edges here.
Unless being paid I will extend features and bugs

However feel free to check and fix bugs.

Happy Python-ing!
