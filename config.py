import ujson
import os

CONFIG_NAME = "digiclk.json"

class Config:
    def __init__(self):
        self.fgcolor_setting = 6
        self.bgcolor_setting = 0
        self.fgcolor = (255, 255, 255)
        self.bgcolor = (0, 0, 0)
        self.themeid = 0

        # check for config file
        if CONFIG_NAME in os.listdir("."):
            self.readConfig()
        else:
            self.writeConfig()

    def readConfig(self):
        with open(CONFIG_NAME, "r") as f:
            try:
                c = ujson.loads(f.read())
                if "fgcolor" in c and isinstance(c["fgcolor"], list):
                    self.fgcolor = c["fgcolor"]
                if "fgcolor_setting" in c and isinstance(c["fgcolor_setting"], int):
                    self.fgcolor_setting = c["fgcolor_setting"]
                if "bgcolor" in c and isinstance(c["bgcolor"], list):
                    self.bgcolor = c["bgcolor"]
                if "bgcolor_setting" in c and isinstance(c["bgcolor_setting"], int):
                    self.bgcolor_setting = c["bgcolor_setting"]
                if "themeid" in c and isinstance(c["themeid"], int):
                    self.themeid = c["themeid"]
            except ValueError:
                print("parsing %s failed" % CONFIG_NAME)

    def writeConfig(self):
        with open(CONFIG_NAME, "w") as f:
            f.write(ujson.dumps({"fgcolor_setting": self.fgcolor_setting, \
                "bgcolor_setting": self.bgcolor_setting, \
                "fgcolor": self.fgcolor, \
                "bgcolor": self.bgcolor, \
                "themeid": self.themeid}))
