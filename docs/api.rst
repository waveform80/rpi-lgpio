.. Copyright (c) 2022 Dave Jones <dave@waveform.org.uk>
..
.. SPDX-License-Identifier: MIT

=============
API Reference
=============

.. module:: RPi.GPIO

The API of rpi-lgpio (naturally) follows that of rpi-gpio (aka RPi.GPIO) as
closely as possible. As such the following is simply a re-iteration of that
API.


Initialization
==============

.. autofunction:: setmode

.. autofunction:: getmode

.. autofunction:: setup

.. autofunction:: cleanup


Pin Usage
=========

.. autofunction:: input

.. autofunction:: output


Edge Detection
==============

.. autofunction:: wait_for_edge

.. autofunction:: add_event_detect

.. autofunction:: add_event_callback

.. autofunction:: event_detected


Miscellaneous
=============

.. autofunction:: gpio_function

.. autofunction:: setwarnings


PWM
===

.. autoclass:: PWM


Constants
=========

.. data:: RPI_INFO

    A dictionary that provides information about the model of Raspberry Pi that
    the library is loaded onto. Includes the following keys:

    P1_REVISION
        The revision of the P1 header. 0 indicates no P1 header (typical on the
        compute module range), 1 and 2 vary on the oldest Raspberry Pi models,
        and 3 is the typical 40-pin header present on all modern Raspberry Pis.

    REVISION
        The hex `board revision code`_ as a :class:`str`.

    TYPE
        The name of the Pi model, e.g. "Pi 4 Model B"

    MANUFACTURER
        The name of the board manufacturer, e.g. "Sony UK"

    PROCESSOR
        The name of the SoC used on the board, e.g. "BCM2711"

    RAM
        The amount of RAM installed on the board, e.g. "4GB"

    The board revision can be overridden with the ``RPI_LGPIO_REVISION``
    environment variable; see :ref:`revision` for further details.

.. data:: RPI_REVISION

    The same as the ``P1_REVISION`` key in :data:`RPI_INFO`

.. _board revision code: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#new-style-revision-codes

.. data:: BOARD

    Indicates to :func:`setmode` that physical board numbering is requested

.. data:: BCM

    Indicates to :func:`setmode` that GPIO numbering is requested

.. data:: PUD_OFF

    Used with :func:`setup` to disable internal pull resistors on an input

.. data:: PUD_DOWN

    Used with :func:`setup` to enable the internal pull-down resistor on an
    input

.. data:: PUD_UP

    Used with :func:`setup` to enable the internal pull-up resistor on an input

.. data:: OUT

    Used with :func:`setup` to set a GPIO to an output, and
    :func:`gpio_function` to report a GPIO is an output

.. data:: IN

    Used with :func:`setup` to set a GPIO to an input, and
    :func:`gpio_function` to report a GPIO is an input

.. data:: HARD_PWM
.. data:: SERIAL
.. data:: I2C
.. data:: SPI

    Used with :func:`gpio_function` to indicate "alternate" modes of certain
    GPIO pins.

    .. note::

        In rpi-lgpio these values will never be returned as the kernel
        device cannot report if pins are in alternate modes.

.. data:: LOW
   :value: 0

    Used with :func:`output` to turn an output GPIO off

.. data:: HIGH
   :value: 1

    Used with :func:`output` to turn an output GPIO on

.. data:: RISING

    Used with :func:`wait_for_edge` and :func:`add_event_detect` to specify
    that rising edges only should be sampled

.. data:: FALLING

    Used with :func:`wait_for_edge` and :func:`add_event_detect` to specify
    that falling edges only should be sampled

.. data:: BOTH

    Used with :func:`wait_for_edge` and :func:`add_event_detect` to specify
    that all edges should be sampled
