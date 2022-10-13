=======================
Differences
=======================

Many of the assumptions underlying RPi.GPIO -- that it has complete access to,
and control over, the registers controlling the GPIO pins -- do not work when
applied to the Linux gpiochip devices. To that end, while the library strives
as far as possible to be "bug compatible" with RPi.GPIO, there *are*
differences in behaviour that may result in incompatibility.


Bug Compatible?
===============

What does being "bug compatible" mean? Simply put it means it is not enough for
the library to implement the RPi.GPIO API. It must also act, as far as is
reasonable possible, like RPi.GPIO too. Naturally it must export the same
functions and classes as RPi.GPIO. However it must also:

* Raise the same exception tyes, with the same messages, in the same
  circumstances

* Break (i.e. fail to operate correctly) in the same way, as far as possible

This may sound silly, but a library is *always* used in unexpected or
undocumented ways by *some* applications and thus anything that tries to take
the place of that library must do more than simply operate the same as the
"documented surface" would suggest.

That said, given that the underlying assumptions are fundamentally different
this will not always be possible...


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
      File "/home/dave/projects/home/rpi-lgpio/rpi-lgpio/RPi/GPIO.py", line 569, in setup
        initial = _check(lgpio.gpio_read(_chip, gpio))
      File "/home/dave/envs/rpi-lgpio/lib/python3.10/site-packages/lgpio.py", line 894, in gpio_read
        return _u2i(_lgpio._gpio_read(handle&0xffff, gpio))
      File "/home/dave/envs/rpi-lgpio/lib/python3.10/site-packages/lgpio.py", line 461, in _u2i
        raise error(error_text(v))
    lgpio.error: 'GPIO not allocated'


.. _debounce

Debounce
========

Debouncing of signals works fundamentally differently RPi.GPIO, and in `lgpio`_
(the library underlying rpi-lgpio). Rather than attempt to add more complexity
in between users and lgpio, which would also inevitably slow down edge
detection (with all the attendant timing issues for certain applications) it is
likely preferable to just live with this difference, but document it
thoroughly.

RPi.GPIO performs debounce by tracking the last timestamp at which it saw a
specified edge and suppressing reports of edges that occur within the specified
number of milliseconds after that.

lgpio (and thus rpi-lgpio) performs debounce by waiting for a signal to be
stable for the specified number of milliseconds before reporting the edge.

For some applications, there will be little/no difference other than rpi-lgpio
reporting an edge a few milliseconds later than RPi.GPIO would (specifically,
by the amount of debounce requsted). The following diagram shows the waveform
from a "bouncy" switch, along with the positions in time where RPi.GPIO and
rpi-lgpio would report the rising edge when debounce of 3ms is requested::

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

However, consider this same scenario if debounce of 2ms is requested::

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
pulses (like PWM) every 2ms::

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

.. _lgpio: https://abyz.me.uk/lg/py_lgpio.html
