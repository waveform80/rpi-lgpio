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

Useful Links
============

* `Source code <https://github.com/waveform80/rpi-lgpio>`_

* `Bug reports <https://github.com/waveform80/rpi-lgpio/issues>`_

* `Documentation <https://rpi-lgpio.readthedocs.io/>`_

* `Ubuntu packaging <https://launchpad.net/ubuntu/+source/rpi-lgpio>`_

.. * `Debian packaging <https://salsa.debian.org/python-team/packages/rpi-lgpio>`_

.. _rpi-gpio: https://pypi.org/project/RPi.GPIO/
.. _gpiochip device: https://embeddedbits.org/new-linux-kernel-gpio-user-space-interface/
.. _deprecated sysfs GPIO interface: https://waldorf.waveform.org.uk/2021/the-pins-they-are-a-changin.html
