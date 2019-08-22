import display
import leds
import buttons
import utime

def ceilDiv(a, b):
    return (a + (b - 1)) // b

def tipHeight(w):
    return ceilDiv(w, 2) - 1

def drawTip(d, x, y, w, c, invert = False, swapAxes = False):
    h = tipHeight(w)
    for dy in range(h):
        for dx in range(dy + 1, w - 1 - dy):
            px = x + dx
            py = y + dy if not invert else y + h - 1 - dy
            if swapAxes:
                px, py = py, px
            d.pixel(px, py, col = c)

def drawSeg(d, x, y, w, h, c, swapAxes = False):
    tip_h = tipHeight(w)
    body_h = h - 2 * tip_h

    drawTip(d, x, y, w, c, invert = True, swapAxes = swapAxes)

    px1, px2 = x, x + w
    py1, py2 = y + tip_h, y + tip_h + body_h
    if swapAxes:
        px1, px2, py1, py2 = py1, py2, px1, px2
    d.rect(px1, py1, px2, py2, col = c)

    drawTip(d, x, y + tip_h + body_h, w, c, invert = False, swapAxes = swapAxes)

def drawVSeg(d, x, y, w, l, c):
    drawSeg(d, x, y, w, l, c)

def drawHSeg(d, x, y, w, l, c):
    drawSeg(d, y, x, w, l, c, swapAxes = True)

def drawGridSeg(d, x, y, w, l, c, swapAxes = False):
    sw = w - 2
    tip_h = tipHeight(sw)

    x = x * w
    y = y * w
    l = (l - 1) * w
    drawSeg(d, x + 1, y + tip_h + 3, sw, l - 3, c, swapAxes = swapAxes)

def drawGridVSeg(d, x, y, w, l, c):
    drawGridSeg(d, x, y, w, l, c)

def drawGridHSeg(d, x, y, w, l, c):
    drawGridSeg(d, y, x, w, l, c, swapAxes = True)

def drawGrid(d, x1, y1, x2, y2, w, c):
    for x in range(x1 * w, x2 * w):
        for y in range(y1 * w, y2 * w):
            if x % w == 0 or x % w == w - 1 or y % w == 0 or y % w == w - 1:
                d.pixel(x, y, col = c)

def drawGrid7Seg(d, x, y, w, segs, c):
    if segs[0]:
        drawGridHSeg(d, x, y, w, 4, c)
    if segs[1]:
        drawGridVSeg(d, x + 3, y, w, 4, c)
    if segs[2]:
        drawGridVSeg(d, x + 3, y + 3, w, 4, c)
    if segs[3]:
        drawGridHSeg(d, x, y + 6, w, 4, c)
    if segs[4]:
        drawGridVSeg(d, x, y + 3, w, 4, c)
    if segs[5]:
        drawGridVSeg(d, x, y, w, 4, c)
    if segs[6]:
        drawGridHSeg(d, x, y + 3, w, 4, c)

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

DISPLAY = 0
CHANGE_HOURS = 1
CHANGE_MINUTES = 2
CHANGE_SECONDS = 3
CHANGE_NAME = 4
MODE = DISPLAY
MODES = {
    DISPLAY: '---',
    CHANGE_HOURS: 'HRS',
    CHANGE_MINUTES: 'MNS',
    CHANGE_SECONDS: 'SEC',
    CHANGE_NAME: 'NAM'
}
NAME = bytearray(b'   yrlf')

def renderNum(d, num, x):
    drawGrid7Seg(d, x, 0, 7, DIGITS[num // 10], (255, 255, 255))
    drawGrid7Seg(d, x + 5, 0, 7, DIGITS[num % 10], (255, 255, 255))

def renderColon(d):
    drawGridVSeg(d, 11, 2, 7, 2, (255, 255, 255))
    drawGridVSeg(d, 11, 4, 7, 2, (255, 255, 255))

def renderText(d, text, blankidx = None):
    bs = bytearray(text)

    if blankidx != None:
        bs[blankidx:blankidx+1] = b'_'

    d.print(MODES[MODE] + ' ' + bs.decode(), fg = (255, 255, 255), bg = None, posx = 0, posy = 7 * 8)

BUTTON_SEL = 1 << 0
BUTTON_UP = 1 << 1
BUTTON_DOWN = 1 << 2
BUTTON_SEL_LONG = 1 << 3
BUTTON_UP_LONG = 1 << 4
BUTTON_DOWN_LONG = 1 << 5
pressed_prev = 0
button_sel_time = 0
button_up_time = 0
button_down_time = 0
def checkButtons():
    global pressed_prev, button_sel_time, button_up_time, button_down_time

    t = utime.time()
    pressed = buttons.read(buttons.BOTTOM_LEFT | buttons.TOP_RIGHT | buttons.BOTTOM_RIGHT)
    cur_buttons = 0

    if pressed & buttons.BOTTOM_LEFT and not pressed_prev & buttons.BOTTOM_LEFT:
        button_sel_time = t
    elif not pressed & buttons.BOTTOM_LEFT and pressed_prev & buttons.BOTTOM_LEFT:
        if button_sel_time < t:
            cur_buttons |= BUTTON_SEL_LONG
        else:
            cur_buttons |= BUTTON_SEL

    if pressed & buttons.TOP_RIGHT and not pressed_prev & buttons.TOP_RIGHT:
        button_sel_time = t
    elif not pressed & buttons.TOP_RIGHT and pressed_prev & buttons.TOP_RIGHT:
        if button_sel_time < t:
            cur_buttons |= BUTTON_UP_LONG
        else:
            cur_buttons |= BUTTON_UP

    if pressed & buttons.BOTTOM_RIGHT and not pressed_prev & buttons.BOTTOM_RIGHT:
        button_sel_time = t
    elif not pressed & buttons.BOTTOM_RIGHT and pressed_prev & buttons.BOTTOM_RIGHT:
        if button_sel_time < t:
            cur_buttons |= BUTTON_DOWN_LONG
        else:
            cur_buttons |= BUTTON_DOWN

    pressed_prev = pressed
    return cur_buttons

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE

WORKAROUND_OFFSET = None
def detect_workaround_offset():
    global WORKAROUND_OFFSET

    old = utime.time()
    utime.set_time(old)
    new = utime.time()

    WORKAROUND_OFFSET = old - new

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
    if bs & BUTTON_UP:
        utime.set_time(utime.time() + HOUR + WORKAROUND_OFFSET)
    if bs & BUTTON_DOWN:
        utime.set_time(utime.time() - HOUR + WORKAROUND_OFFSET)

def ctrl_chg_mns(bs):
    global MODE
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_SECONDS
    if bs & BUTTON_UP:
        utime.set_time(utime.time() + MINUTE + WORKAROUND_OFFSET)
    if bs & BUTTON_DOWN:
        utime.set_time(utime.time() - MINUTE + WORKAROUND_OFFSET)

def ctrl_chg_sec(bs):
    global MODE, name_idx
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_NAME
        name_idx = 0
    if bs & BUTTON_UP:
        utime.set_time(utime.time() + SECOND + WORKAROUND_OFFSET)
    if bs & BUTTON_DOWN:
        utime.set_time(utime.time() - SECOND + WORKAROUND_OFFSET)

name_idx = 0
def ctrl_chg_nam(bs):
    global MODE, name_idx
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_HOURS
        name_idx = 0
    # TODO

CTRL_FNS = {
    DISPLAY: ctrl_display,
    CHANGE_HOURS: ctrl_chg_hrs,
    CHANGE_MINUTES: ctrl_chg_mns,
    CHANGE_SECONDS: ctrl_chg_sec,
    CHANGE_NAME: ctrl_chg_nam
}

def render(d):
    ltime = utime.localtime()
    hours = ltime[3]
    mins = ltime[4]
    secs = ltime[5]

    d.clear()
    #drawGrid(d, 1, 0, 22, 7, 7, (255, 0, 0))

    if MODE != CHANGE_HOURS or secs % 2 == 0:
        renderNum(d, hours, 1)

    if secs % 2 == 0:
        renderColon(d)

    if MODE != CHANGE_MINUTES or secs % 2 == 0:
        renderNum(d, mins, 13)

    renderText(d, NAME, None)

    d.update()

def main():
    try:
        detect_workaround_offset()
        with display.open() as d:
            while True:
                bs = checkButtons()
                CTRL_FNS[MODE](bs)
                render(d)
    except KeyboardInterrupt:
        pass

main()
