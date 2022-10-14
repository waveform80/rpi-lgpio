======
README
======

rpi-lgpio is a compatibility package intended to provide compatibility with
the `rpi-gpio`_ (aka RPi.GPIO) library, on top of kernels that only support the
`gpiochip device`_ (and which have removed the `deprecated sysfs GPIO
interface`_).

.. warning::

    You *cannot* install rpi-lgpio and `rpi-gpio`_ (aka RPi.GPIO, the library
    it emulates) at the same time, in the same Python environment. Both
    packages attempt to install a module named ``RPi.GPIO`` and obviously this
    will not work.

.. _rpi-gpio: https://pypi.org/project/RPi.GPIO/
.. _gpiochip device: https://embeddedbits.org/new-linux-kernel-gpio-user-space-interface/
.. _deprecated sysfs GPIO interface: https://waldorf.waveform.org.uk/2021/the-pins-they-are-a-changin.html
