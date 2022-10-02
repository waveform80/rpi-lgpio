import warnings

import lgpio

UNKNOWN = -1
BOARD = 10
BCM = 11

PUD_OFF = 20
PUD_DOWN = 21
PUD_UP = 22

OUT = 0
IN = 1
LOW = 0
HIGH = 1

RISING = 31
FALLING = 32
BOTH = 33

SERIAL = 40
SPI = 41
I2C = 42
HARD_PWM = 43

# Note the nuance of the early boards (in which GPIO0/1 and GPIO2/3 were
# switched) is not represented here. This library (currently) has no intention
# of supporting the early Pi boards. As such, this mapping only represents the
# Pi Model B+ onwards
_BOARD_MAP = {
    3: 2, 5: 3, 7: 4, 8: 14, 10: 15, 11: 17, 12: 18, 13: 27, 15: 22, 16: 23,
    18: 24, 19: 10, 21: 9, 22: 25, 23: 11, 24: 8, 26: 7, 29: 5, 31: 6, 32: 12,
    33: 13, 35: 19, 36: 16, 37: 26, 38: 20, 40: 21,
}

_mode = UNKNOWN
_chip = None
_reserved = {}
_warnings = True


def _check(result):
    # Many lgpio functions return <0 on error; this simple function just
    # converts any result<0 to the appropriate RuntimeError message and passes
    # non-negative results back to the caller
    if result < 0:
        raise RuntimeError(lgpio.error_text(result))
    return result


def _to_gpio(channel):
    if _mode == UNKNOWN:
        raise RuntimeError(
            'Please set pin numbering mode using GPIO.setmode(GPIO.BOARD) or '
            'GPIO.setmode(GPIO.BCM)')
    elif _mode == BCM:
        return channel
    elif _mode == BOARD:
        return _BOARD_MAP[channel]
    else:
        assert False, 'Invalid channel mode'


def _gpio_list(chanlist):
    # Convert chanlist which may be an iterable, or an int, to a tuple of
    # integers
    try:
        return tuple(_to_gpio(int(channel)) for channel in chanlist)
    except TypeError:
        try:
            return (_to_gpio(int(chanlist)),)
        except TypeError:
            raise ValueError(
                'Channel must be an integer or list/tuple of integers')


def _in_use(gpio):
    # LG bits (256, 512, 1024, 2048) are only set if the calling process owns
    # the GPIO
    return bool(_check(lgpio.gpio_get_mode(_chip, gpio)) & 0b111100000000)


def getmode():
    """
    Get the numbering mode used for the pins on the board. Returns
    :data:`BOARD`, :data:`BCM` or :data:`None`.
    """

    if _mode == UNKNOWN:
        return None
    else:
        return _mode


def setmode(new_mode):
    """
    Set up the numbering mode to use for the pins on the board. The options
    for *new_mode* are:

    * :data:`BOARD` - Use Raspberry Pi board numbers
    * :data:`BCM` - Use Broadcom GPIO 00..nn numbers

    If a numbering mode has already been set, and *new_mode* is not the same
    as the result of :func:`getmode`, a :exc:`ValueError` is raised.

    :param int new_mode:
        The new numbering mode to apply
    """
    # TODO atexit cleanup of claimed GPIOs to input
    global _mode, _chip

    if _mode != UNKNOWN and new_mode != _mode:
        raise ValueError('A different mode has already been set!')
    if new_mode not in (BOARD, BCM):
        raise ValueError('An invalid mode was passed to setmode()')

    if _chip is None:
        _chip = _check(lgpio.gpiochip_open(0))
    _mode = new_mode


def setwarnings(value):
    """
    Enable or disable warning messages. These are mostly produced when calling
    :func:`setup` or :func:`cleanup` to change channel modes.
    """
    global _warnings
    _warnings = bool(value)


def cleanup(chanlist=None):
    if _chip is None:
        return

    # If we're cleaning up everything we need to close the chip handle too,
    # and reset the GPIO mode. But first...
    close = chanlist is None
    if chanlist is None:
        # It's awfully tempting to just re-initialize here, but that doesn't
        # reset pins to inputs, and users may be relying upon this behaviour
        result, gpios, * = lgpio.gpio_get_chip_info(_chip)
        _check(result)
        chanlist = [gpio for gpio in range(gpios) if _in_use(gpio)]
    else:
        chanlist = _gpio_list(chanlist)

    for gpio in chanlist:
        # As this is cleanup we ignore all errors (no _check calls); if we
        # didn't own the GPIO, we don't care
        lgpio.gpio_claim_input(_chip, gpio, lgpio.SET_BIAS_DISABLE)
        lgpio.gpio_free(_chip, gpio)

    if close:
        global _chip, _mode
        lgpio.gpiochip_close(_chip)
        _chip = None
        _mode = UNKNOWN


def setup(chanlist, direction, pull_up_down=None, initial=None):
    """
    Set up a GPIO channel or iterable of channels with a direction and
    (optionally, for inputs) pull/up down control, or (optionally, for outputs)
    and initial state.

    The GPIOs to affect are listed in *chanlist* which may be any iterable. The
    *direction* is either :data:`IN` or :data:`OUT`.

    If *direction* is :data:`IN`, then *pull_up_down* may specify one of the
    values :data:`PUD_UP` to set the internal pull-up resistor,
    :data:`PUD_DOWN` to set the internal pull-down resistor, or the default
    :data:`PUD_OFF` which disables the internal pulls.

    If *direction* is :data:`OUT`, then *initial* may specify zero or one to
    indicate the initial state of the output.

    :type chanlist: list or tuple or int
    :param chanlist:
        The list of GPIO channels to setup

    :param int direction:
        Whether the channels should act as inputs or outputs

    :type pull_up_down: int or None
    :param pull_up_down:
        The internal pull resistor (if any) to enable for inputs

    :type initial: bool or int or None
    :param initial:
        The initial state of an output
    """
    if direction == OUT:
        if pull_up_down is not None:
            raise ValueError('pull_up_down parameter is not valid for outputs')
        if initial is not None:
            initial = bool(initial)
    elif direction == IN:
        if initial is not None:
            raise ValueError('initial parameter is not valid for inputs')
        if pull_up_down is None:
            pull_up_down = PUD_OFF
        elif pull_up_down not in (PUD_UP, PUD_DOWN, PUD_OFF):
            raise ValueError(
                'Invalid value for pull_up_down - should be either PUD_OFF, '
                'PUD_UP or PUD_DOWN')
    else:
        raise ValueError('An invalid direction was passed to setup()')

    for gpio in _gpio_list(chanlist):
        _setup_one(gpio, direction, pull_up_down, initial)


def _setup_one(gpio, direction, pull, initial):
    # We don't bother with warnings about GPIOs already in use here because
    # if we try to *use* a GPIO already in use, things are going to blow up
    # shortly anyway. We do deal with the pull-up warning, but only for GPIO2
    # and GPIO3 because we're not supporting the original RPi so we don't need
    # to worry about the GPIO0 and GPIO1 discrepancy
    if _warnings and gpio in (2, 3) and pull in (PUD_UP, PUD_DOWN):
        warnings.warn(
            Warning('A physical pull up resistor is fitted on this channel!'))

    if direction == IN:
        _check(lgpio.gpio_claim_input(_chip, gpio, {
            PUD_OFF:  lgpio.SET_BIAS_DISABLE,
            PUD_DOWN: lgpio.SET_BIAS_PULL_DOWN,
            PUD_UP:   lgpio.SET_BIAS_PULL_UP,
        }[pull]))
    elif direction == OUT:
        if initial is None:
            initial = _check(lgpio.gpio_read(_chip, gpio))
        _check(lgpio.gpio_claim_output(
            _chip, gpio, initial, lgpio.SET_BIAS_DISABLE))
    else:
        assert False, 'Invalid direction'


def input(channel):
    """
    Input from a GPIO *channel*. Returns 1 or 0.

    This can also be called on a GPIO output, in which case the value
    returned will be the last state set on the GPIO.

    :param int channel:
        The board pin number or BCM number depending on :func:`setmode`.
    """
    gpio = _to_gpio(channel)
    if not _in_use(gpio):
        raise RuntimeError('You must setup() the GPIO channel first')
    return _check(lgpio.gpio_read(_chip, gpio))


def output(channel, value):
    """
    Output to a GPIO *channel* or list of channels. The *value* can be the
    integer :data:`LOW` or :data:`HIGH`, or a list of integers.

    If a list of channels is specified, with a single integer for the *value*
    then it is applied to all channels. Otherwise, the length of the two lists
    must match.

    :type channel: list or tuple or int
    :param channel:
        The GPIO channel, or list of GPIO channels to output to

    :type value: list or tuple or int
    :param value:
        The value, or list of values to output
    """
    gpios = _gpio_list(channel)
    try:
        values = tuple(bool(item) for item in value)
    except TypeError:
        try:
            values = (bool(value),)
        except TypeError:
            raise ValueError(
                'Value must be an integer/boolean or list/tuple of '
                'integers/booleans')
    if len(gpios) != len(values):
        if len(gpios) > 1 and len(values) == 1:
            values = values * len(gpios)
        else:
            raise RuntimeError('Number of channels != number of values')
    for gpio, value in zip(gpios, values):
        _check(lgpio.gpio_write(_chip, gpio, value))

