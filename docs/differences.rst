.. Copyright (c) 2022-2023 Dave Jones <dave@waveform.org.uk>
..
.. SPDX-License-Identifier: MIT

=======================
Differences
=======================

.. currentmodule:: RPi.GPIO

Many of the assumptions underlying `RPi.GPIO`_ -- that it has complete access
to, and control over, the registers controlling the GPIO pins -- do not work
when applied to the Linux gpiochip devices. To that end, while the library
strives as far as possible to be "bug compatible" with RPi.GPIO, there *are*
differences in behaviour that may result in incompatibility.


Bug Compatible?
===============

What does being "bug compatible" mean? It is not enough for the library to
implement the `RPi.GPIO`_ API. It must also:

* Act, as far as possible, in the same way to the same calls with the same
  values

* Raise the same exception types, with the same messages, in the same
  circumstances

* Break (i.e. fail to operate correctly) in the same way, as far as possible

This last point may sound silly, but a library is *always* used in unexpected
or undocumented ways by *some* applications. Thus anything that tries to take
the place of that library must do more than simply operate the same as the
"documented surface" would suggest.

That said, given that the underlying assumptions are fundamentally different
this will not always be possible...


.. _revision:

Pi Revision
===========

The RPi.GPIO module attempts to determine the revision of Raspberry Pi board
that it is running on when the module is imported by querying
:file:`/proc/cpuinfo`, raising :exc:`RuntimeError` at import time if it finds
it is not running on a Raspberry Pi. rpi-lgpio emulates this behaviour, but
this can be inconvenient for certain situations including testing, and usage of
rpi-lgpio on other single board computers.

To that end rpi-lgpio permits a Raspberry Pi `revision code`_ to be manually
specified via the environment in the ``RPI_LGPIO_REVISION`` value (when this is
set, :file:`/proc/cpuinfo` is not read at all). For example:

.. code-block:: console

    $ RPI_LGPIO_REVISION="c03114" python3
    Python 3.10.6 (main, Aug 10 2022, 11:40:04) [GCC 11.3.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from RPi import GPIO
    >>> GPIO.RPI_INFO
    {'P1_REVISION': 3, 'REVISION': 'c03114', 'TYPE': 'Pi 4 Model B',
    'MANUFACTURER': 'Sony UK', 'PROCESSOR': 'BCM2711', 'RAM': '4GB'}
    >>> exit()
    $ RPI_LGPIO_REVISION="902120" python3
    Python 3.10.6 (main, Aug 10 2022, 11:40:04) [GCC 11.3.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from RPi import GPIO
    >>> GPIO.RPI_INFO
    {'P1_REVISION': 3, 'REVISION': '902120', 'TYPE': 'Zero 2 W',
    'MANUFACTURER': 'Sony UK', 'PROCESSOR': 'BCM2837', 'RAM': '512M'}
    >>> exit()

At present, rpi-lgpio only interprets "`new-style`_" (6 hex-digit) revision
codes, as found in the "Revision" field of :file:`/proc/cpuinfo`. The
`old-style`_ (4 hex-digit) revision codes found on the original model B, A, A+,
B+, and Compute Module 1 are not supported. If there is significant demand,
this can be added but for the time being only boards made since the launch of
the 2B (which introduced the new-style revision codes) are supported.
Specifically, this includes the following models:

* Zero

* Zero W

* Zero 2W

* 2B

* 3B

* Compute Module 3

* 3A+

* 3B+

* Compute Module 3+

* 4B

* 400

* Compute Module 4

* 5B

A workaround for use on old-style boards is to use ``RPI_LGPIO_REVISION`` to
fake the revision code. For example, 0004 (an old-style model B rev 2) can also
be represented by 800012 in the new-style.

.. code-block:: console

    $ RPI_LGPIO_REVISION="800012" python3
    Python 3.12.2 (main, Apr  2 2024, 18:40:52) [GCC 13.2.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from RPi import GPIO
    >>> GPIO.RPI_INFO
    {'P1_REVISION': 2, 'REVISION': '800012', 'TYPE': 'Model B',
    'MANUFACTURER': 'Sony UK', 'PROCESSOR': 'BCM2835', 'RAM': '256M'}
    >>> exit()

.. _revision code: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#new-style-revision-codes
.. _new-style: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#new-style-revision-codes
.. _old-style: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#old-style-revision-codes


.. _gpio_chip:

GPIO Chip
=========

The lgpio library needs to know the number of the ``/dev/gpiochip`` device it
should open. By default this will be calculated from the reported
:ref:`revision` (which may be customized as detailed in that section). In
practice this means the chip defaults to "4" on the Raspberry Pi Model 5B, and
"0" on all other boards.

You may also specify the chip manually using the ``RPI_LGPIO_CHIP`` environment
variable. For example:

.. code-block:: console

    $ ls /dev/gpiochip*
    crw-------  1 root root    254, 0 Oct  1 15:00 /dev/gpiochip0
    crw-------  1 root root    254, 1 Oct  1 15:00 /dev/gpiochip1
    crw-------  1 root root    254, 2 Oct  1 15:00 /dev/gpiochip2
    crw-------  1 root root    254, 3 Oct  1 15:00 /dev/gpiochip3
    crw-rw----+ 1 root dialout 254, 4 Oct  1 15:00 /dev/gpiochip4
    crw-------  1 root root    254, 5 Oct  1 15:00 /dev/gpiochip5
    $ RPI_LGPIO_CHIP=5 python3
    Python 3.11.5 (main, Aug 29 2023, 15:31:31) [GCC 13.2.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from RPi import GPIO
    >>> GPIO.setmode(GPIO.BCM)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/usr/lib/python3/dist-packages/RPi/GPIO/__init__.py", line 513, in setmode
        _chip = _check(lgpio.gpiochip_open(int(chip_num)))
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/lib/python3/dist-packages/lgpio.py", line 645, in gpiochip_open
        return _u2i(handle)
               ^^^^^^^^^^^^
      File "/usr/lib/python3/dist-packages/lgpio.py", line 458, in _u2i
        raise error(error_text(v))
    lgpio.error: 'can not open gpiochip'

This is primarily useful for other boards where the correct gpiochip device is
something other than 0.


Alternate Pin Modes
===================

The :func:`gpio_function` function can be used to report the current mode of a
pin. In RPi.GPIO this may return several "alternate" mode values including
:data:`SPI`, :data:`I2C`, and :data:`HARD_PWM`. rpi-lgpio will only ever return
the basic :data:`IN` and :data:`OUT` values however, as the underlying gpiochip
device cannot report alternate modes.

For example, under RPi.GPIO:

.. code-block:: pycon

    >>> from RPi import GPIO
    >>> GPIO.setmode(GPIO.BCM)
    >>> GPIO.gpio_function(2) == GPIO.I2C
    True

Under rpi-lgpio:

.. code-block:: pycon

    >>> from RPi import GPIO
    >>> GPIO.setmode(GPIO.BCM)
    >>> GPIO.gpio_function(2) == GPIO.I2C
    False
    >>> GPIO.gpio_function(2) == GPIO.IN
    True


Stack Traces
============

While every effort has been made to raise the same exceptions with the same
messages as RPi.GPIO, rpi-lgpio does raise the exceptions from pure Python so
the exceptions will generally include a larger stack trace than under RPi.GPIO.
For example, under RPi.GPIO:

.. code-block:: pycon

    >>> from RPi import GPIO
    >>> GPIO.setmode(GPIO.BCM)
    >>> GPIO.setup(26, GPIO.IN)
    >>> GPIO.output(26, 1)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    RuntimeError: The GPIO channel has not been set up as an OUTPUT

Under rpi-lgpio:

.. code-block:: pycon

    >>> from RPi import GPIO
    >>> GPIO.setmode(GPIO.BCM)
    >>> GPIO.setup(26, GPIO.IN)
    >>> GPIO.output(26, 1)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/home/dave/projects/rpi-lgpio/rpi-lgpio/RPi/GPIO.py", line 626, in output
        _check_output(mode, 'The GPIO channel has not been set up as an OUTPUT')
      File "/home/dave/projects/rpi-lgpio/rpi-lgpio/RPi/GPIO.py", line 242, in _check_output
        raise RuntimeError(msg)
    RuntimeError: The GPIO channel has not been set up as an OUTPUT


Simultaneous Access
===================

Two processes using RPi.GPIO can happily control the same pin. This is simply
not permitted by the Linux gpiochip device and will fail under rpi-lgpio. For
example, if another process has reserved GPIO26, and our script also tries to
allocate it:

.. code-block:: pycon

    >>> from RPi import GPIO
    >>> GPIO.setmode(GPIO.BCM)
    >>> GPIO.setup(26, GPIO.OUT)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/home/dave/projects/rpi-lgpio/rpi-lgpio/RPi/GPIO.py", line 569, in setup
        initial = _check(lgpio.gpio_read(_chip, gpio))
      File "/home/dave/envs/rpi-lgpio/lib/python3.10/site-packages/lgpio.py", line 894, in gpio_read
        return _u2i(_lgpio._gpio_read(handle&0xffff, gpio))
      File "/home/dave/envs/rpi-lgpio/lib/python3.10/site-packages/lgpio.py", line 461, in _u2i
        raise error(error_text(v))
    lgpio.error: 'GPIO not allocated'

How can you tell if a GPIO is reserved by another process? Use the
:manpage:`gpioinfo(1)` tool, which is part of the ``gpiod`` package. By default
this attempts to read GPIO chip 0, which is fine all Pi's *except* the Pi 5
where you will need to read GPIO chip 4 specifically:

.. code-block:: console

    $ gpioinfo 4
    gpiochip4 - 54 lines:
        line   0:     "ID_SDA"       unused   input  active-high
        line   1:     "ID_SCL"       unused   input  active-high
        line   2:      "GPIO2"       unused   input  active-high
        line   3:      "GPIO3"       unused   input  active-high
        line   4:      "GPIO4"       unused   input  active-high
        line   5:      "GPIO5"       unused   input  active-high
        line   6:      "GPIO6"       unused   input  active-high
        line   7:      "GPIO7"   "spi0 CS1"  output   active-low [used]
        line   8:      "GPIO8"   "spi0 CS0"  output   active-low [used]
        line   9:      "GPIO9"       unused   input  active-high
        line  10:     "GPIO10"       unused   input  active-high
        line  11:     "GPIO11"       unused   input  active-high
        line  12:     "GPIO12"       unused   input  active-high
        line  13:     "GPIO13"       unused   input  active-high
        line  14:     "GPIO14"       unused   input  active-high
        line  15:     "GPIO15"       unused   input  active-high
        line  16:     "GPIO16"       unused   input  active-high
        line  17:     "GPIO17"       unused   input  active-high
        line  18:     "GPIO18"       unused   input  active-high
        line  19:     "GPIO19"       unused   input  active-high
        line  20:     "GPIO20"       unused   input  active-high
        line  21:     "GPIO21"       unused   input  active-high
        line  22:     "GPIO22"       unused   input  active-high
        line  23:     "GPIO23"       unused   input  active-high
        line  24:     "GPIO24"       unused   input  active-high
        line  25:     "GPIO25"       unused   input  active-high
        line  26:     "GPIO26"       unused   input  active-high
        line  27:     "GPIO27"       unused   input  active-high
        line  28: "PCIE_RP1_WAKE" unused output active-high
        line  29:   "FAN_TACH"       unused   input  active-high
        line  30:   "HOST_SDA"       unused   input  active-high
        line  31:   "HOST_SCL"       unused   input  active-high
        line  32:  "ETH_RST_N"  "phy-reset"  output   active-low [used]
        line  33:          "-"       unused   input  active-high
        line  34: "CD0_IO0_MICCLK" "cam0_reg" output active-high [used]
        line  35: "CD0_IO0_MICDAT0" unused input active-high
        line  36: "RP1_PCIE_CLKREQ_N" unused input active-high
        line  37:          "-"       unused   input  active-high
        line  38:    "CD0_SDA"       unused   input  active-high
        line  39:    "CD0_SCL"       unused   input  active-high
        line  40:    "CD1_SDA"       unused   input  active-high
        line  41:    "CD1_SCL"       unused   input  active-high
        line  42: "USB_VBUS_EN" unused output active-high
        line  43:   "USB_OC_N"       unused   input  active-high
        line  44: "RP1_STAT_LED" "PWR" output active-low [used]
        line  45:    "FAN_PWM"       unused  output  active-high
        line  46: "CD1_IO0_MICCLK" "cam1_reg" output active-high [used]
        line  47:  "2712_WAKE"       unused   input  active-high
        line  48: "CD1_IO1_MICDAT1" unused input active-high
        line  49: "EN_MAX_USB_CUR" unused output active-high
        line  50:          "-"       unused   input  active-high
        line  51:          "-"       unused   input  active-high
        line  52:          "-"       unused   input  active-high
        line  53:          "-"       unused   input  active-high

The ``[used]`` suffixes indicate which GPIOs are reserved by other processes.
In the output above we can see that GPIOs 7 and 8 are reserved. As it happens,
these are reserved by the kernel because we have ``dtparam=spi=on`` in our boot
configuration to enable the kernel SPI devices (:file:`/dev/spidev0.0` and
:file:`/dev/spidev0.1`). As a result, these GPIOs *cannot* be used by rpi-lgpio
because the kernel will not let anything else reserve them. They can only be
used for SPI via those kernel devices, and the only way to release those GPIOs
would be to change our kernel / boot configuration.

In other cases we may find that a GPIO is temporarily reserved by a process.
For example, the following trivial script will reserve GPIO21.

.. code-block:: python3

    from time import sleep
    from RPi import GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21, GPIO.OUT)
    while True:
        sleep(1)

If we again query :manpage:`gpioinfo(1)` while it is running we will see the
following:

.. code-block:: console

    $ gpioinfo 4 | grep GPIO21
            line  21:     "GPIO21"         "lg"  output  active-high [used bias-disabled]

However, this reservation will disappear when the process dies.

.. note::

    If you receive the ``GPIO not allocated`` error in your script, please
    check the output of :manpage:`gpioinfo(1)` to see if the GPIO you want to
    use is reserved by something else.


.. _debounce:

Debounce
========

Debouncing of signals works fundamentally differently in RPi.GPIO, and in
`lgpio`_ (the library underlying rpi-lgpio). Rather than attempt to add more
complexity in between users and lgpio, which would also inevitably slow down
edge detection (with all the attendant timing issues for certain applications)
it is likely preferable to just live with this difference, but document it
thoroughly.

RPi.GPIO debounces signals by tracking the last timestamp at which it saw a
specified edge and suppressing reports of edges that occur within the specified
number of milliseconds after that.

lgpio (and thus rpi-lgpio) debounces by waiting for a signal to be stable for
the specified number of milliseconds before reporting the edge.

For some applications, there will be little/no difference other than rpi-lgpio
reporting an edge a few milliseconds later than RPi.GPIO would (specifically,
by the amount of debounce requsted). The following diagram shows the waveform
from a "bouncy" switch being pressed once, along with the points in time where
RPi.GPIO and rpi-lgpio would report the rising edge when debounce of 3ms is
requested:

.. code-block::
   :class: chart

    0ms    2ms     4ms     6ms     8ms
    |      |       |       |       |
    |      ┌─┐ ┌─┐ ┌─────────────────┐
    |      │ │ │ │ │           :     │
    |      │ │ │ │ │           :     │
    ───────┘ └─┘ └─┘           :     └────────────────────────
           :                   :
           :                   :
        RPi.GPIO             rpi-lgpio

RPi.GPIO reports the edge at 2ms, then suppresses the edges at 3ms and 4ms
because they are within 3ms of the last edge. By contrast, rpi-lgpio ignores
the first and second rising edges (because they didn't stay stable for 3ms) and
only reports the third edge at 7ms (after it's spent 3ms stable).

However, consider this same scenario if debounce of 2ms is requested:

.. code-block::
   :class: chart

    0ms    2ms     4ms     6ms     8ms
    |      |       |       |       |
    |      ┌─┐ ┌─┐ ┌─────────────────┐
    |      │ │ │ │ │       :         │
    |      │ │ │ │ │       :         │
    ───────┘ └─┘ └─┘       :         └────────────────────────
           :       :       :
           :       :       :
       RPi.GPIO  RPi.GPIO  rpi-lgpio

In this case, RPi.GPIO reports the switch *twice* because the third edge is
at least 2ms after the first edge. However, rpi-lgpio only reports the switch
*once* because only one edge stayed stable for 2ms. Also note in this case,
that rpi-lgpio's report time has moved back to 6ms because it's not waiting as
long for stability.

.. note::

    This implies that you may find shorter debounce periods preferable when
    working with rpi-lgpio, than with RPi.GPIO. They will still debounce
    effectively, but will reduce the delay in reporting edges.

One final scenario to consider is a waveform of equally spaced, repeating
pulses (like PWM) every 2ms:

.. code-block::
   :class: chart

    0ms    2ms     4ms     6ms     8ms     10ms    12ms
    |      |       |       |       |       |       |
    |      ┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌──
    |      │    │  │    │  │    │  │    │  │    │  │    │  │
    |      │    │  │    │  │    │  │    │  │    │  │    │  │
    ───────┘    └──┘    └──┘    └──┘    └──┘    └──┘    └──┘
           :               :               :               :
           :               :               :               :
      RPi.GPIO        RPi.GPIO        RPi.GPIO        RPi.GPIO

If we request rising edge detection with a debounce of 3ms, RPi.GPIO reports
half of the edges; it's suppressing every other edge as they occur within 3ms
of the edge preceding them. rpi-lgpio, on the other hand, reports *no* edges at
all because none of them stay stable for 3ms.


PWM on inputs
=============

RPi.GPIO (probably erroneously) permits PWM objects to continue operating on
pins that are switched to inputs:

.. code-block:: pycon

    >>> from RPi import GPIO
    >>> GPIO.setmode(GPIO.BCM)
    >>> GPIO.setup(26, GPIO.OUT)
    >>> p = GPIO.PWM(26, 1000)
    >>> p.start(75)
    >>> GPIO.setup(26, GPIO.IN)
    >>> p.stop()
    >>> p.start(75)
    >>> p.stop()

This will not work under rpi-lgpio:

.. code-block:: pycon

    >>> from RPi import GPIO
    >>> GPIO.setmode(GPIO.BCM)
    >>> GPIO.setup(26, GPIO.OUT)
    >>> p = GPIO.PWM(26, 1000)
    >>> p.start(75)
    >>> GPIO.setup(26, GPIO.IN)
    >>> p.stop()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/home/dave/projects/rpi-lgpio/rpi-lgpio/RPi/GPIO.py", line 190, in stop
        lgpio.tx_pwm(_chip, self._gpio, 0, 0)
      File "/home/dave/envs/rpi-lgpio/lib/python3.10/site-packages/lgpio.py", line 1074, in tx_pwm
        return _u2i(_lgpio._tx_pwm(
      File "/home/dave/envs/rpi-lgpio/lib/python3.10/site-packages/lgpio.py", line 461, in _u2i
        raise error(error_text(v))
    lgpio.error: 'bad PWM micros'

Though note that the error occurs when the :class:`PWM` object is *next* acted
upon, rather than at the point when the GPIO is switched to an input.


.. _RPi.GPIO: https://pypi.org/project/RPi.GPIO/
.. _lgpio: https://abyz.me.uk/lg/py_lgpio.html
