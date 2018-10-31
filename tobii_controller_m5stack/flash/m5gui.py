from m5stack import lcd
from m5ui import *


class TextBox:

    def __init__(self, x_pos, y_pos, width, height, txt="",
                 v_align=0, h_align=lcd.CENTER,
                 text_color = 0xffffff, bg_color=0x000000, text_font=lcd.FONT_Default):
        self.x = x_pos
        self.y = y_pos
        self.width = width
        self.height = height
        self.vAlign = v_align
        self.hAlign = h_align
        self.text = txt
        self.textFont = text_font
        self.textColor = text_color
        self.bgColor = bg_color

        self.redraw_self()

    def redraw_self(self):
        lcd.setwin(self.x, self.y, self.x + self.width, self.y + self.height)
        lcd.clearwin(self.bgColor)
        lcd.font(self.textFont, transparent=True)
        lcd.text(self.hAlign, self.vAlign, self.text, self.textColor)

    def setText(self, txt, color = lcd.WHITE):
        self.textColor = color
        self.text = txt
        self.redraw_self()


class LogBox:

    def __init__(self, x_pos, y_pos, width, height, text_color=0xcccccc, bg_color=0x000000, text_font=lcd.FONT_Default):
        self.x = x_pos
        self.y = y_pos
        self.width = width
        self.height = height
        self.textFont = text_font
        self.textColor = text_color
        self.bgColor = bg_color
        self.cursor = (0, 0)

        lcd.setwin(self.x, self.y, self.x + self.width, self.y + self.height)
        lcd.clearwin(self.bgColor)

    def update(self, text):
        lcd.setwin(self.x, self.y, self.x + self.width, self.y + self.height)

        if self.cursor[1] + lcd.fontSize()[1] >= self.height:
            self.cursor = (0, 0)
            lcd.clearwin(self.bgColor)

        lcd.setCursor(self.cursor[0], self.cursor[1])
        lcd.font(self.textFont, transparent=True)
        lcd.print(text)
        self.cursor = (lcd.getCursor()[0]-self.x, lcd.getCursor()[1]-self.y)


maxx, maxy = lcd.screensize()
col_width = int(maxx / 3)
line_height = int(maxy / 18)

lcd.clear()
btnA = M5Button(name='ButtonA', text='New', visibility=True)
btnB = M5Button(name='ButtonB', text='Calibrate', visibility=True)
btnC = M5Button(name='ButtonC', text='REC', visibility=True)


# Tobii Glasses Column Title
tobii_title_lbl = TextBox(0, 0, col_width*2, line_height*2, "Tobii Glasses",
                          lcd.CENTER, text_font=lcd.FONT_DejaVu18, text_color=0x88d600)

# Connection status box
tobi_ip_box = TextBox(0, 39, col_width*2, line_height*2, "not connected", v_align=lcd.CENTER)

#  Recording details titles
tobii_project_lbl = TextBox(0, 78, int(col_width*2/3), line_height, "Proj:")
tobii_participant_lbl = TextBox(int(col_width*2/3), 78, int(col_width*2/3), line_height, "User:")
tobii_calibration_lbl = TextBox(int(col_width*2/3)*2, 78, int(col_width*2/3), line_height, "Calib:")

#Recording details value boxes
tobii_project_val_box = TextBox(0, 91, int(col_width*2/3), line_height, "-")
tobii_participant_val_box = TextBox(int(col_width*2/3), 91, int(col_width*2/3), line_height, "-")
tobii_calibration_val_box = TextBox(int(col_width*2/3)*2, 91, int(col_width*2/3), line_height, "-")

# MAIN Status Box
tobii_status_box = TextBox(0, 110, col_width*2, line_height*2, "---", v_align=lcd.CENTER,
                           text_color=lcd.GREEN, text_font=lcd.FONT_DejaVu18)

# Sensors column title
sensors_title_lbl = TextBox(col_width*2, 0, col_width, line_height*2, "Sensors",
                            lcd.CENTER, text_font=lcd.FONT_DejaVu18, text_color=0x88d600)

# Sensor names labels
sensor_a_lbl = TextBox(col_width*2, 39, col_width, line_height, "LUX")
sensor_b_lbl = TextBox(col_width*2, 78, col_width, line_height, "Sensor X", text_color=0x555555)
sensor_c_lbl = TextBox(col_width*2, 117, col_width, line_height, "Sensor Y", text_color=0x555555)

# Sensor Value boxes
sensor_a_val_box = TextBox(col_width*2, 52, col_width, line_height, "00000.00", v_align=1)
sensor_b_val_box = TextBox(col_width*2, 91, col_width, line_height, "---", v_align=1, text_color=0x555555)
sensor_c_val_box = TextBox(col_width*2, 130, col_width, line_height, "---", v_align=1, text_color=0x555555)

# General Log Box
log_box = LogBox(0, 150, col_width*3, line_height*4, bg_color=0x262729)

lcd.setCursor(0, 0)