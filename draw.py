from globals import *

def _ceilDiv(a, b):
    return (a + (b - 1)) // b

def TipHeight(w):
    return _ceilDiv(w, 2) - 1

def Tip(d, x, y, w, c, invert = False, swapAxes = False):
    h = TipHeight(w)
    for dy in range(h):
        for dx in range(dy + 1, w - 1 - dy):
            px = x + dx
            py = y + dy if not invert else y + h - 1 - dy
            if swapAxes:
                px, py = py, px
            d.pixel(px, py, col = c)

def Seg(d, x, y, w, h, c, swapAxes = False):
    tip_h = TipHeight(w)
    body_h = h - 2 * tip_h

    Tip(d, x, y, w, c, invert = True, swapAxes = swapAxes)

    px1, px2 = x, x + w
    py1, py2 = y + tip_h, y + tip_h + body_h
    if swapAxes:
        px1, px2, py1, py2 = py1, py2, px1, px2
    d.rect(px1, py1, px2 - 1, py2 - 1, col = c)

    Tip(d, x, y + tip_h + body_h, w, c, invert = False, swapAxes = swapAxes)

def VSeg(d, x, y, w, l, c):
    Seg(d, x, y, w, l, c)

def HSeg(d, x, y, w, l, c):
    Seg(d, y, x, w, l, c, swapAxes = True)

def GridSeg(d, x, y, w, l, c, swapAxes = False):
    sw = w - 2
    tip_h = TipHeight(sw)

    x = x * w
    y = y * w
    l = (l - 1) * w
    Seg(d, x + 1, y + tip_h + 3, sw, l - 3, c, swapAxes = swapAxes)

def GridVSeg(d, x, y, w, l, c):
    GridSeg(d, x, y, w, l, c)

def GridHSeg(d, x, y, w, l, c):
    GridSeg(d, y, x, w, l, c, swapAxes = True)

def Grid(d, x1, y1, x2, y2, w, c):
    for x in range(x1 * w, x2 * w):
        for y in range(y1 * w, y2 * w):
            if x % w == 0 or x % w == w - 1 or y % w == 0 or y % w == w - 1:
                d.pixel(x, y, col = c)

def Grid7Seg(d, x, y, w, segs, c):
    if segs[0]:
        GridHSeg(d, x, y, w, 4, c)
    if segs[1]:
        GridVSeg(d, x + 3, y, w, 4, c)
    if segs[2]:
        GridVSeg(d, x + 3, y + 3, w, 4, c)
    if segs[3]:
        GridHSeg(d, x, y + 6, w, 4, c)
    if segs[4]:
        GridVSeg(d, x, y + 3, w, 4, c)
    if segs[5]:
        GridVSeg(d, x, y, w, 4, c)
    if segs[6]:
        GridHSeg(d, x, y + 3, w, 4, c)

def renderNum(d, num, x, c):
    Grid7Seg(d, x, 0, 7, DIGITS[num // 10], c)
    Grid7Seg(d, x + 5, 0, 7, DIGITS[num % 10], c)

def renderColon(d, c):
    GridVSeg(d, 11, 2, 7, 2, c)
    GridVSeg(d, 11, 4, 7, 2, c)

def renderBar(d, num, c):
    d.rect(20, 78, 20 + num * 2, 80, col = c)

def renderTime(d, ltime, mode, c):
    years = ltime[0]
    months = ltime[1]
    days = ltime[2]
    hours = ltime[3]
    mins = ltime[4]
    secs = ltime[5]

    if mode == CHANGE_YEAR:
        renderNum(d, years // 100, 1, c)
        renderNum(d, years % 100, 13, c)
    elif mode == CHANGE_MONTH:
        renderNum(d, months, 13, c)
    elif mode == CHANGE_DAY:
        renderNum(d, days, 13, c)
    else:
        renderNum(d, hours, 1, c)
        renderNum(d, mins, 13, c)

    if mode not in (CHANGE_YEAR, CHANGE_MONTH, CHANGE_DAY) and secs % 2 == 0:
        renderColon(d, c)

    renderBar(d, secs, c)
