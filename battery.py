import os
import power

battery_color_good = (0, 230, 0)
battery_color_ok   = (255, 215, 0)
battery_color_bad  = (255, 0, 0)

BATTERY_FLASH = [None, None, None, [3], [2, 3], [1, 2], [2, 3], [1, 2], [1], None, None, None, None]

def get_bat_color():
    """
    Function determines the color of the battery indicator. Colors can be set in config.
    Voltage threshold's are currently estimates as voltage isn't that great of an indicator for
    battery charge.
    :return: false if old firmware, RGB color array otherwise
    """
    try:
        v = os.read_battery()
        if v > 3.8:
            return battery_color_good
        if v > 3.6:
            return battery_color_ok
        return battery_color_bad
    except AttributeError:
        return None


def render_battery(disp):
    """
    Adds the battery indicator to the display. Does not call update or clear so it can be used in addition to
    other display code.
    :param disp: open display
    """
    c = get_bat_color()
    if not c:
        return
    disp.line(141, 62, 155, 62, col = c)
    disp.line(155, 62, 155, 68, col = c)
    disp.line(155, 68, 141, 68, col = c)
    disp.line(141, 68, 141, 62, col = c)
    disp.rect(156, 64, 157, 66, filled = True, col = c)
    try:
        charging = (power.read_chargein_voltage() > 1)
    except AttributeError:
        charging = False
    try:
        v = os.read_battery()
        fillWidth = round(max(min(v - 3.6, 0.44), 0) * 32.5)
        if not charging:
            disp.rect(142, 63, 141 + fillWidth, 67, filled = True, col = c)
        else:
            for i in range(13):
                if not BATTERY_FLASH[i]:
                    if fillWidth > i:
                        disp.line(142 + i, 63, 142 + i, 67, col = c)
                else:
                    if fillWidth > i:
                        y = min(BATTERY_FLASH[i]) - 2
                        if y >= 0:
                            disp.line(142 + i, 63, 142 + i, 63 + y, col = c)
                        y = max(BATTERY_FLASH[i]) + 2
                        if y <= 4:
                            disp.line(142 + i, 63 + y, 142 + i, 68, col = c)
                    for y in BATTERY_FLASH[i]:
                        disp.pixel(142 + i, 63 + y, col = c)
    except AttributeError:
        return
