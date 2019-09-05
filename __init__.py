import os
import sys
import leds
import display
import buttons

sys.path.append('/apps/digiclk/')
import monotime as utime
import draw
import nicesegments
import config
import battery
from globals import *

THEMES = [draw, nicesegments]

def renderText(d, text, blankidx = None):
    bs = bytearray(text)

    if blankidx != None:
        bs[blankidx:blankidx+1] = b'_'

    if MODE == DISPLAY:
        t = bs.decode()[:10]
    else:
        t = MODES[MODE] + ' ' + bs.decode()[:6]

    d.print(t, fg = conf.fgcolor, bg = conf.bgcolor, posx = 0, posy = 7 * 8)

def render(d):
    ltime = utime.localtime()
    years = ltime[0]
    months = ltime[1]
    days = ltime[2]
    secs = ltime[5]

    d.clear(col = conf.bgcolor)

    theme.renderTime(d, ltime, MODE, conf.fgcolor)

    if SUBMODE == DATE and MODE == DISPLAY:
        renderText(d, str(years) + '-' + str(months) + '-' + str(days), None)
    else:
        renderText(d, NAME, None)

    battery.render_battery(d)

    d.update()

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
    global MODE, SUBMODE, updated
    updated = True
    if bs & BUTTON_SEL_LONG:
        MODE = CHANGE_HOURS
    elif bs & BUTTON_UP or bs & BUTTON_DOWN:
        # this needs to be more specific when having more submodes
        if SUBMODE == NICK:
            SUBMODE = DATE
        else:
            SUBMODE = NICK
    else:
        updated = False

def ctrl_chg_hrs(bs):
    global MODE, updated
    updated = True
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    elif bs & BUTTON_SEL:
        MODE = CHANGE_MINUTES
    elif bs & BUTTON_UP_LONG:
        modTime(0, 0, 0, 10, 0, 0)
    elif bs & BUTTON_DOWN_LONG:
        modTime(0, 0, 0, -10, 0, 0)
    elif bs & BUTTON_UP:
        modTime(0, 0, 0, 1, 0, 0)
    elif bs & BUTTON_DOWN:
        modTime(0, 0, 0, -1, 0, 0)
    else:
        updated = False

def ctrl_chg_mns(bs):
    global MODE, updated
    updated = True
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    elif bs & BUTTON_SEL:
        MODE = CHANGE_SECONDS
    elif bs & BUTTON_UP_LONG:
        modTime(0, 0, 0, 0, 10, 0)
    elif bs & BUTTON_DOWN_LONG:
        modTime(0, 0, 0, 0, -10, 0)
    elif bs & BUTTON_UP:
        modTime(0, 0, 0, 0, 1, 0)
    elif bs & BUTTON_DOWN:
        modTime(0, 0, 0, 0, -1, 0)
    else:
        updated = False

def ctrl_chg_sec(bs):
    global MODE, updated
    updated = True
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    elif bs & BUTTON_SEL:
        MODE = CHANGE_YEAR
    elif bs & BUTTON_UP_LONG:
        modTime(0, 0, 0, 0, 0, 10)
    elif bs & BUTTON_DOWN_LONG:
        modTime(0, 0, 0, 0, 0, -10)
    elif bs & BUTTON_UP:
        modTime(0, 0, 0, 0, 0, 1)
    elif bs & BUTTON_DOWN:
        modTime(0, 0, 0, 0, 0, -1)
    else:
        updated = False

def ctrl_chg_yrs(bs):
    global MODE, updated
    updated = True
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    elif bs & BUTTON_SEL:
        MODE = CHANGE_MONTH
    elif bs & BUTTON_UP_LONG:
        modTime(10, 0, 0, 0, 0, 0)
    elif bs & BUTTON_DOWN_LONG:
        modTime(-10, 0, 0, 0, 0, 0)
    elif bs & BUTTON_UP:
        modTime(1, 0, 0, 0, 0, 0)
    elif bs & BUTTON_DOWN:
        modTime(-1, 0, 0, 0, 0, 0)
    else:
        updated = False

def ctrl_chg_mth(bs):
    global MODE, updated
    updated = True
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    elif bs & BUTTON_SEL:
        MODE = CHANGE_DAY
    elif bs & BUTTON_UP_LONG:
        modTime(0, 6, 0, 0, 0, 0)
    elif bs & BUTTON_DOWN_LONG:
        modTime(0, -6, 0, 0, 0, 0)
    elif bs & BUTTON_UP:
        modTime(0, 1, 0, 0, 0, 0)
    elif bs & BUTTON_DOWN:
        modTime(0, -1, 0, 0, 0, 0)
    else:
        updated = False

def ctrl_chg_day(bs):
    global MODE, updated
    updated = True
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    elif bs & BUTTON_SEL:
        MODE = CHANGE_THEME
    elif bs & BUTTON_UP_LONG:
        modTime(0, 0, 10, 0, 0, 0)
    elif bs & BUTTON_DOWN_LONG:
        modTime(0, 0, -10, 0, 0, 0)
    elif bs & BUTTON_UP:
        modTime(0, 0, 1, 0, 0, 0)
    elif bs & BUTTON_DOWN:
        modTime(0, 0, -1, 0, 0, 0)
    else:
        updated = False

def ctrl_chg_thm(bs):
    global MODE, updated
    updated = True
    global theme
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    elif bs & BUTTON_SEL:
        MODE = CHANGE_FGCOLOR
    elif bs & BUTTON_UP:
        conf.themeid += 1
        if conf.themeid >= len(THEMES):
            conf.themeid = 0
    elif bs & BUTTON_DOWN:
        conf.themeid -= 1
        if conf.themeid < 0:
            conf.themeid = len(THEMES) - 1
    else:
        updated = False
    if bs & BUTTON_UP or bs & BUTTON_DOWN:
        theme = THEMES[conf.themeid]

def ctrl_chg_fgc(bs):
    global MODE, updated
    updated = True
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    elif bs & BUTTON_SEL:
        MODE = CHANGE_BGCOLOR
    elif bs & BUTTON_UP:
        conf.fgcolor_setting += 1
        if conf.fgcolor_setting >= len(COLORS):
            conf.fgcolor_setting = 0
    elif bs & BUTTON_DOWN:
        conf.fgcolor_setting -= 1
        if conf.fgcolor_setting < 0:
            conf.fgcolor_setting = len(COLORS) - 1
    else:
        updated = False
    if bs & BUTTON_UP or bs & BUTTON_DOWN:
        conf.fgcolor = COLORS[conf.fgcolor_setting]

def ctrl_chg_bgc(bs):
    global MODE, updated
    updated = True
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    elif bs & BUTTON_SEL:
        MODE = CHANGE_HOURS
    elif bs & BUTTON_UP:
        conf.bgcolor_setting += 1
        if conf.bgcolor_setting >= len(COLORS):
            conf.bgcolor_setting = 0
    elif bs & BUTTON_DOWN:
        conf.bgcolor_setting -= 1
        if conf.bgcolor_setting < 0:
            conf.bgcolor_setting = len(COLORS) - 1
    else:
        updated = False
    if bs & BUTTON_UP or bs & BUTTON_DOWN:
        conf.bgcolor = COLORS[conf.bgcolor_setting]

NAME = None
FILENAME = 'nickname.txt'
def load_nickname():
    global NAME
    if FILENAME in os.listdir('.'):
        with open("nickname.txt", "rb") as f:
            NAME = f.read().strip()
    else:
        NAME = b''

MODE = DISPLAY
SUBMODE = NICK

updated = False

CTRL_FNS = {
    DISPLAY: ctrl_display,
    CHANGE_HOURS: ctrl_chg_hrs,
    CHANGE_MINUTES: ctrl_chg_mns,
    CHANGE_SECONDS: ctrl_chg_sec,
    CHANGE_YEAR: ctrl_chg_yrs,
    CHANGE_MONTH: ctrl_chg_mth,
    CHANGE_DAY: ctrl_chg_day,
    CHANGE_THEME: ctrl_chg_thm,
    CHANGE_FGCOLOR: ctrl_chg_fgc,
    CHANGE_BGCOLOR: ctrl_chg_bgc,
}

def main():
    global conf
    global theme
    global updated
    try:
        load_nickname()
        conf = config.Config()
        theme = THEMES[conf.themeid]
        with display.open() as d:
            last_secs, secs = 0, 0
            last_msecs, msecs = 0, 0
            while True:
                updated = False

                bs = checkButtons()
                saveConfig = (MODE != DISPLAY)
                CTRL_FNS[MODE](bs)
                if saveConfig and MODE == DISPLAY:
                    conf.writeConfig() # store config on leaving settings

                last_secs, secs = secs, utime.time_monotonic()
                if updated or secs > last_secs:
                    render(d)

                last_msecs, msecs = msecs, utime.time_monotonic_ms()
                if msecs - last_msecs < BUTTON_UPDATE_TIME:
                    utime.sleep_ms(BUTTON_UPDATE_TIME - (msecs - last_msecs))
    except KeyboardInterrupt:
        pass

main()
