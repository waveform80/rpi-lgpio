.. Copyright (c) 2022 Dave Jones <dave@waveform.org.uk>
..
.. SPDX-License-Identifier: MIT

============
Installation
============

rpi-lgpio is distributed in several formats. The following sections detail
installation from a variety of formats. But first a warning:

.. warning::

    You *cannot* install rpi-lgpio and rpi-gpio (aka RPi.GPIO, the library it
    emulates) at the same time, in the same Python environment. Both packages
    attempt to install a module named ``RPi.GPIO`` and obviously this will not
    work.


apt/deb package
===============

If your distribution includes rpi-lgpio in its archive of apt packages, then
you can simply:

.. code-block:: console

    $ sudo apt remove python3-rpi.gpio
    $ sudo apt install python3-rpi-lgpio

If you wish to go back to rpi-gpio:

.. code-block:: console

    $ sudo apt remove python3-rpi-lgpio
    $ sudo apt install python3-rpi.gpio


wheel package
=============

If your distribution does not include a "native" packaging of rpi-lgpio, you
can also install using pip:

.. code-block:: console

    $ pip uninstall rpi-gpio
    $ pip install rpi-lgpio

On some platforms you may need to use a Python 3 specific alias of pip:

.. code-block:: console

    $ pip3 uninstall rpi-gpio
    $ pip3 install rpi-lgpio

The instructions above assume that rpi-gpio is already installed by pip as
well, but this may not be the case. For instance, you may have rpi-gpio
installed from, say, apt, but your particular distro doesn't also include
rpi-lgpio. In this case you may need to remove rpi-gpio from apt first:

.. code-block:: console

    $ sudo apt remove python3-rpi.gpio
    $ pip3 install rpi-lgpio

If you wish to install system-wide with pip, you may need to place ``sudo`` in
front of the ``pip`` (or ``pip3``) commands too.
