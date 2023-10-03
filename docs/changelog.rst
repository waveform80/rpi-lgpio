.. Copyright (c) 2022-2023 Dave Jones <dave@waveform.org.uk>
..
.. SPDX-License-Identifier: MIT

==========
Changelog
==========

.. currentmodule:: RPi.GPIO


Release 0.4 (2023-10-03)
========================

* Add compatibility with Raspberry Pi 5 (auto-selection of correct gpiochip
  device)
* Add ability to override gpiochip selection; see :ref:`gpio_chip`
* Convert bouncetime -666 to :data:`None` (bug compatibility, which also
  ensures this should work with GPIO Zero's rpigpio pin driver)
* Fix ``pull_up_down`` default on :func:`setup`


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
