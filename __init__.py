import os
import sys
import leds
import display
import buttons

sys.path.append('/apps/digiclk/')
import monotime as utime
import nicesegments
import config

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

def renderNum(d, num, x):
    nicesegments.Grid7Seg(d, x, 2, DIGITS[num // 10], conf.fgcolor)
    nicesegments.Grid7Seg(d, x + 22, 2, DIGITS[num % 10], conf.fgcolor)

def renderColon(d):
    nicesegments.GridColon(d, 46, 2, conf.fgcolor)
    nicesegments.GridColon(d, 102, 2, conf.fgcolor)

def renderText(d, text, blankidx = None):
    bs = bytearray(text)

    if blankidx != None:
        bs[blankidx:blankidx+1] = b'_'

    d.print(((MODES[MODE] + ' ') if MODE != DISPLAY else '') + bs.decode(), \
        fg = conf.fgcolor, bg = conf.bgcolor, posx = 0, posy = 7 * 8)

def render(d):
    ltime = utime.localtime()
    years = ltime[0]
    months = ltime[1]
    days = ltime[2]
    hours = ltime[3]
    mins = ltime[4]
    secs = ltime[5]

    d.clear(col = conf.bgcolor)

    if MODE == CHANGE_YEAR:
        renderNum(d, years // 100, 2)
        renderNum(d, years % 100, 58)
    elif MODE == CHANGE_MONTH:
        renderNum(d, months, 58)
    elif MODE == CHANGE_DAY:
        renderNum(d, days, 58)
    else:
        renderNum(d, hours, 2)
        renderNum(d, mins, 58)
        renderNum(d, secs, 114)

    if MODE not in (CHANGE_YEAR, CHANGE_MONTH, CHANGE_DAY) and secs % 2 == 0:
        renderColon(d)

    if MODE == DISPLAY and int(secs / 10) % 2 == 0:
        renderText(d, str(years) + '-' + str(months) + '-' + str(days), None)
    else:
        renderText(d, NAME, None)

    d.update()

LONG_DELAY = 400
BUTTON_SEL = 1 << 0
BUTTON_SEL_LONG = 1 << 1
BUTTON_UP = 1 << 2
BUTTON_UP_LONG = 1 << 3
BUTTON_DOWN = 1 << 4
BUTTON_DOWN_LONG = 1 << 5
pressed_prev = 0
button_long_prev = {
    BUTTON_SEL: False,
    BUTTON_UP: False,
    BUTTON_DOWN: False
}
button_times = {
    BUTTON_SEL: 0,
    BUTTON_UP: 0,
    BUTTON_DOWN: 0
}
def checkButton(button, button_long, osbutton, pressed, t):
    cur_buttons = 0

    if pressed & osbutton and not pressed_prev & osbutton:
        button_times[button] = t
        button_long_prev[button] = False
    elif pressed_prev & osbutton:
        if button_times[button] + LONG_DELAY < t:
            cur_buttons |= button_long
            button_times[button] = t
            button_long_prev[button] = True
        elif not pressed & osbutton and not button_long_prev[button]:
            cur_buttons |= button

    return cur_buttons

def checkButtons():
    global pressed_prev

    t = utime.time_monotonic_ms()
    pressed = buttons.read(buttons.BOTTOM_LEFT | buttons.TOP_RIGHT | buttons.BOTTOM_RIGHT)
    cur_buttons = 0

    cur_buttons |= checkButton(BUTTON_SEL, BUTTON_SEL_LONG, buttons.BOTTOM_LEFT, pressed, t)
    cur_buttons |= checkButton(BUTTON_UP, BUTTON_UP_LONG, buttons.TOP_RIGHT, pressed, t)
    cur_buttons |= checkButton(BUTTON_DOWN, BUTTON_DOWN_LONG, buttons.BOTTOM_RIGHT, pressed, t)

    pressed_prev = pressed
    return cur_buttons

def modTime(yrs, mth, day, hrs, mns, sec):
    ltime = utime.localtime()
    new = utime.mktime((ltime[0] + yrs, ltime[1] + mth, ltime[2] + day, ltime[3] + hrs, ltime[4] + mns, ltime[5] + sec, None, None))
    utime.set_time(new)

def ctrl_display(bs):
    global MODE
    if bs & BUTTON_SEL_LONG:
        MODE = CHANGE_HOURS

def ctrl_chg_hrs(bs):
    global MODE
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_MINUTES
    if bs & BUTTON_UP_LONG:
        modTime(0, 0, 0, 10, 0, 0)
    if bs & BUTTON_DOWN_LONG:
        modTime(0, 0, 0, -10, 0, 0)
    if bs & BUTTON_UP:
        modTime(0, 0, 0, 1, 0, 0)
    if bs & BUTTON_DOWN:
        modTime(0, 0, 0, -1, 0, 0)

def ctrl_chg_mns(bs):
    global MODE
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_SECONDS
    if bs & BUTTON_UP_LONG:
        modTime(0, 0, 0, 0, 10, 0)
    if bs & BUTTON_DOWN_LONG:
        modTime(0, 0, 0, 0, -10, 0)
    if bs & BUTTON_UP:
        modTime(0, 0, 0, 0, 1, 0)
    if bs & BUTTON_DOWN:
        modTime(0, 0, 0, 0, -1, 0)

def ctrl_chg_sec(bs):
    global MODE
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_YEAR
    if bs & BUTTON_UP_LONG:
        modTime(0, 0, 0, 0, 0, 10)
    if bs & BUTTON_DOWN_LONG:
        modTime(0, 0, 0, 0, 0, -10)
    if bs & BUTTON_UP:
        modTime(0, 0, 0, 0, 0, 1)
    if bs & BUTTON_DOWN:
        modTime(0, 0, 0, 0, 0, -1)

def ctrl_chg_yrs(bs):
    global MODE
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_MONTH
    if bs & BUTTON_UP_LONG:
        modTime(10, 0, 0, 0, 0, 0)
    if bs & BUTTON_DOWN_LONG:
        modTime(-10, 0, 0, 0, 0, 0)
    if bs & BUTTON_UP:
        modTime(1, 0, 0, 0, 0, 0)
    if bs & BUTTON_DOWN:
        modTime(-1, 0, 0, 0, 0, 0)

def ctrl_chg_mth(bs):
    global MODE
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_DAY
    if bs & BUTTON_UP_LONG:
        modTime(0, 6, 0, 0, 0, 0)
    if bs & BUTTON_DOWN_LONG:
        modTime(0, -6, 0, 0, 0, 0)
    if bs & BUTTON_UP:
        modTime(0, 1, 0, 0, 0, 0)
    if bs & BUTTON_DOWN:
        modTime(0, -1, 0, 0, 0, 0)

def ctrl_chg_day(bs):
    global MODE
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_FGCOLOR
    if bs & BUTTON_UP_LONG:
        modTime(0, 0, 10, 0, 0, 0)
    if bs & BUTTON_DOWN_LONG:
        modTime(0, 0, -10, 0, 0, 0)
    if bs & BUTTON_UP:
        modTime(0, 0, 1, 0, 0, 0)
    if bs & BUTTON_DOWN:
        modTime(0, 0, -1, 0, 0, 0)

def ctrl_chg_fgcol(bs):
    global MODE
    global conf
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_BGCOLOR
    if bs & BUTTON_UP:
        conf.fgcolor_setting += 1
        if conf.fgcolor_setting >= len(COLORS):
            conf.fgcolor_setting = 0
    if bs & BUTTON_DOWN:
        conf.fgcolor_setting -= 1
        if conf.fgcolor_setting < 0:
            conf.fgcolor_setting = len(COLORS) - 1
    if bs & BUTTON_UP or bs & BUTTON_DOWN:
        conf.fgcolor = COLORS[conf.fgcolor_setting]
        conf.writeConfig()

def ctrl_chg_bgcol(bs):
    global MODE
    global conf
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_HOURS
    if bs & BUTTON_UP:
        conf.bgcolor_setting += 1
        if conf.bgcolor_setting >= len(COLORS):
            conf.bgcolor_setting = 0
    if bs & BUTTON_DOWN:
        conf.bgcolor_setting -= 1
        if conf.bgcolor_setting < 0:
            conf.bgcolor_setting = len(COLORS) - 1
    if bs & BUTTON_UP or bs & BUTTON_DOWN:
        conf.bgcolor = COLORS[conf.bgcolor_setting]
        conf.writeConfig()

NAME = None
FILENAME = 'nickname.txt'
def load_nickname():
    global NAME
    if FILENAME in os.listdir('.'):
        with open("nickname.txt", "rb") as f:
            name = f.read().strip()
    else:
        name = b'no nick'

    if len(name) > 7:
        name = name[0:7]
    else:
        name = b' ' * (7 - len(name)) + name

    NAME = name

# MODE values
DISPLAY = 0
CHANGE_HOURS = 1
CHANGE_MINUTES = 2
CHANGE_SECONDS = 3
CHANGE_YEAR = 4
CHANGE_MONTH = 5
CHANGE_DAY = 6
CHANGE_FGCOLOR = 7
CHANGE_BGCOLOR = 8

MODE = DISPLAY
MODES = {
    DISPLAY: '---',
    CHANGE_HOURS: 'HRS',
    CHANGE_MINUTES: 'MNS',
    CHANGE_SECONDS: 'SEC',
    CHANGE_YEAR: 'YRS',
    CHANGE_MONTH: 'MTH',
    CHANGE_DAY: 'DAY',
    CHANGE_FGCOLOR: 'FGCOL',
    CHANGE_BGCOLOR: 'BGCOL'
}

CTRL_FNS = {
    DISPLAY: ctrl_display,
    CHANGE_HOURS: ctrl_chg_hrs,
    CHANGE_MINUTES: ctrl_chg_mns,
    CHANGE_SECONDS: ctrl_chg_sec,
    CHANGE_YEAR: ctrl_chg_yrs,
    CHANGE_MONTH: ctrl_chg_mth,
    CHANGE_DAY: ctrl_chg_day,
    CHANGE_FGCOLOR: ctrl_chg_fgcol,
    CHANGE_BGCOLOR: ctrl_chg_bgcol,
}

def main():
    global conf
    try:
        load_nickname()
        conf = config.Config()
        with display.open() as d:
            while True:
                bs = checkButtons()
                CTRL_FNS[MODE](bs)
                render(d)
    except KeyboardInterrupt:
        pass

main()
