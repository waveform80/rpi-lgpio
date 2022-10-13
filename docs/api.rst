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
