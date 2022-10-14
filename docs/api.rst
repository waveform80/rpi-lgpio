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

    Used with :func:`setup` to set a GPIO to an output

.. data:: IN

    Used with :func:`setup` to set a GPIO to an input

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
