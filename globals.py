COLORS = [(0,0,0),(255,0,0),(255,255,0),(0,255,0),(0,255,255),(0,0,255),(255,255,255),(130,30,70),(0,80,0),(0,80,80)]

DIGITS = [
    (True, True, True, True, True, True, False),
    (False, True, True, False, False, False, False),
    (True, True, False, True, True, False, True),
    (True, True, True, True, False, False, True),
    (False, True, True, False, False, True, True),
    (True, False, True, True, False, True, True),
    (True, False, True, True, True, True, True),
    (True, True, True, False, False, False, False),
    (True, True, True, True, True, True, True),
    (True, True, True, True, False, True, True)
]

LONG_DELAY = 400
BUTTON_SEL = 1 << 0
BUTTON_SEL_LONG = 1 << 1
BUTTON_UP = 1 << 2
BUTTON_UP_LONG = 1 << 3
BUTTON_DOWN = 1 << 4
BUTTON_DOWN_LONG = 1 << 5

# MODE values
DISPLAY = 0
CHANGE_HOURS = 1
CHANGE_MINUTES = 2
CHANGE_SECONDS = 3
CHANGE_YEAR = 4
CHANGE_MONTH = 5
CHANGE_DAY = 6
CHANGE_THEME = 7
CHANGE_FGCOLOR = 8
CHANGE_BGCOLOR = 9

MODES = {
    DISPLAY: '---',
    CHANGE_HOURS: 'HRS',
    CHANGE_MINUTES: 'MNS',
    CHANGE_SECONDS: 'SEC',
    CHANGE_YEAR: 'YRS',
    CHANGE_MONTH: 'MTH',
    CHANGE_DAY: 'DAY',
    CHANGE_THEME: 'THM',
    CHANGE_FGCOLOR: 'FGC',
    CHANGE_BGCOLOR: 'BGC'
}
