.. Copyright (c) 2022 Dave Jones <dave@waveform.org.uk>
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

The RPi.GPIO module attempts to determine the model and revision of Raspberry
Pi board that it is running on when the module is imported, raising
:exc:`RuntimeError` at import time if it finds it is not running on a Raspberry
Pi. rpi-lgpio emulates this behaviour, but this can be inconvenient for certain
situations including testing, but also usage of rpi-lgpio on other single board
computers.

To that end rpi-lgpio permits a Raspberry Pi `revision code`_ to be manually
specified via the environment in the ``RPI_LGPIO_REVISION`` value. For example:

.. code-block:: console

    $ RPI_LGPIO_REVISION='c03114' python3
    Python 3.10.6 (main, Aug 10 2022, 11:40:04) [GCC 11.3.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from RPi import GPIO
    >>> GPIO.RPI_INFO
    {'P1_REVISION': 3, 'REVISION': 'c03114', 'TYPE': 'Pi 4 Model B',
    'MANUFACTURER': 'Sony UK', 'PROCESSOR': 'BCM2711', 'RAM': '4GB'}
    >>> exit()
    $ RPI_LGPIO_REVISION='902120' python3
    Python 3.10.6 (main, Aug 10 2022, 11:40:04) [GCC 11.3.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from RPi import GPIO
    >>> GPIO.RPI_INFO
    {'P1_REVISION': 3, 'REVISION': '902120', 'TYPE': 'Zero 2 W',
    'MANUFACTURER': 'Sony UK', 'PROCESSOR': 'BCM2837', 'RAM': '512M'}
    >>> exit()

.. _revision code: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#new-style-revision-codes


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
from a "bouncy" switch being pressed once, along with the positions in time
where RPi.GPIO and rpi-lgpio would report the rising edge when debounce of 3ms
is requested:

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
still 2ms after the first edge. However, rpi-lgpio only reports the switch
*once* because only one edge stayed stable for 2ms. Also note in this case,
that rpi-lgpio's report time has moved back to 6ms because it's not waiting as
long for stability.

This implies that you may find shorter debounce periods preferable when working
with rpi-lgpio, than with RPi.GPIO. They will still debounce effectively, but
will reduce the delay in reporting edges.

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
