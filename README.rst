======
README
======

The rpi-lgpio is a compatibility package intended to provide compatibility with
the rpi-gpio (aka RPi.GPIO) library, on top of kernels that only support the
gpiochip interface (and which have removed the deprecated sysfs GPIO
interface).

.. warning::

    You *cannot* install rpi-lgpio and rpi-gpio at the same time, in the same
    Python environment. Both packages attempt to install a module named
    RPi.GPIO and obviously this will not work.


