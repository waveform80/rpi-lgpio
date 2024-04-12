.. Copyright (c) 2022-2023 Dave Jones <dave@waveform.org.uk>
..
.. SPDX-License-Identifier: MIT

==========
Changelog
==========

.. currentmodule:: RPi.GPIO


Release 0.5 (2024-04-12)
========================

* Fix setting pull on GPIO2 & 3 (`#8`_)
* Added some bits to the Differences chapter on determining which GPIOs are
  reserved

.. _#8: https://github.com/waveform80/rpi-lgpio/pull/8


Release 0.4 (2023-10-03)
========================

* Add compatibility with Raspberry Pi 5 (auto-selection of correct gpiochip
  device)
* Add ability to override gpiochip selection; see :ref:`gpio_chip`
* Convert bouncetime -666 to :data:`None` (bug compatibility, which also
  ensures this should work with GPIO Zero's rpigpio pin driver)
* Fix ``pull_up_down`` default on :func:`setup`
* Fix changing ``pull_up_down`` of already-acquired input
* Ensure :meth:`PWM.stop` is idempotent


Release 0.3 (2022-10-14)
========================

* Permit override of Pi revision code; see :ref:`revision`
* Document alternate pin modes in :doc:`differences`


Release 0.2 (2022-10-14)
========================

* Add support for :data:`RPI_REVISION` and :data:`RPI_INFO` globals


Release 0.1 (2022-10-14)
========================

* Initial release
