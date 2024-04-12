.. Copyright (c) 2022 David Vescovi <dvescovi@tampabay.rr.com>
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

    $ sudo apt install python3-rpi-lgpio

If you wish to go back to rpi-gpio:

.. code-block:: console

    $ sudo apt remove python3-rpi-lgpio
    $ sudo apt install python3-rpi.gpio


wheel package
=============

If your distribution does not include a "native" packaging of rpi-lgpio, you
can also install `rpi-lgpio from PyPI <https://pypi.org/project/rpi-lgpio/>`_
using pip. Please note that rpi-lgpio does still depend on `lgpio
<https://pypi.org/project/lgpio/>`_ so you will need that installed as a
dependency.

.. note::

    It is strongly recommended that you install in a virtualenv if persuing
    this method, in which case you have a choice as to whether lgpio is
    provided by a system package (such as apt), or another wheel.

The following sections demonstrate installing from a wheel in a variety of
scenarios.


in venv without system packages
-------------------------------

Construct a "clean" virutalenv with no access to system packages, then install
rpi-lgpio as a wheel within that virtualenv, trusting it to pull an appropriate
lgpio dependency from PyPI as another wheel:

.. code-block:: console

    $ python3 -m venv cleanvenv
    $ source cleanvenv/bin/activate
    (cleanvenv) $ pip3 install rpi-lgpio


in venv with system packages
----------------------------

Install the lgpio dependency as a system package, construct a virtualenv with
access to system packages, and install rpi-lgpio as a wheel within that
virtualenv:

.. code-block:: console

    $ sudo apt install python3-lgpio
    $ sudo apt remove python3-rpi.gpio
    $ python3 -m venv --system-site-packages sysvenv
    $ source sysvenv/bin/activate
    (sysvenv) $ pip3 install rpi-lgpio

Note that in this case we also ensure that we remove any system-level RPi.GPIO
installation that may interfere.


outside venv (system-wide)
--------------------------

If you wish to install system-wide with pip, you may need to place ``sudo`` in
front of the ``pip`` (or ``pip3``) commands too. Please be aware that on modern
versions of pip you will need to explicitly accept the risk of trying to
co-exist ``apt`` and ``pip`` packages as follows:

.. code-block:: console

    $ sudo pip3 install --break-system-packages rpi-lgpio

.. warning::

    This is not an advised mode of installation, unless you are quite certain
    that you know what pip is going to pull in. Upgrading such an installation
    is also particularly risky.
