import tkinter as tk
from idlelib.tooltip import Hovertip
from random import randint

HEIGH = 25 * 15 + 90
WIDTH = 450
BG_COLOR = "#28323B"
TEXT_COLORS = ["#F37934", "#3E7ECA", "#DDDDDD"]
FONT = ("Arial", 14)

class MyTip(Hovertip):

    def __init__(self, anchor_widget, text, hover_delay=1000, bg="#28323B",
                 foreground="#7FA4B0", font=("Arial", 14)):
        super(MyTip, self).__init__(anchor_widget, text,
                                    hover_delay=hover_delay)
        self.bg = bg
        self.font = font
        self.foreground = foreground
        self.xpos = self.ypos = 0

        self._id4 = self.anchor_widget.bind("<Motion>", self._move_event)

    def __del__(self):
        try:
            self.anchor_widget.unbind("<Motion>", self._id4)
        except tk.TclError:
            pass
        super(MyTip, self).__del__()
    
    def update_pos(self, event=None):
        self.xpos = event.x + 10
        self.ypos = event.y + 10

    def _show_event(self, event=None):
        self.update_pos(event)
        super(MyTip, self)._show_event(event)

    def _move_event(self, event=None):
        if not self.tipwindow:
            self._show_event(event)
            return
        self.update_pos(event)
        root_x = self.anchor_widget.winfo_rootx() + self.xpos
        root_y = self.anchor_widget.winfo_rooty() + self.ypos
        self.tipwindow.wm_geometry("+%d+%d" % (root_x, root_y))

    def get_position(self):
        return self.xpos, self.ypos

    def showcontents(self):
        label = tk.Label(self.tipwindow, text=self.text, foreground=self.foreground,
                         background=self.bg, font=self.font,
                         justify=tk.LEFT, relief=tk.SOLID, borderwidth=0)
        label.pack()

class ScrollList():

    def __init__(self, anchor_widget, labelsCount: int, header: str = None):
        if header:
            self.header = tk.StringVar()
            self.header.set(header)
        else: self.header = None
        self.anchor_widget = anchor_widget
        self.labelsCount = labelsCount

        self.headerHeight = 30
        self.labelHeight = 25
        self.labelWidth = 50
        self.font = ("Arial", )
        self.bg = BG_COLOR
        self.foreground = TEXT_COLORS[2]
        self.hground = TEXT_COLORS[1]
        self._expand = False if header else True

        self.items = []
        self.currItem = 0
        self.tips = []
        
        self.frame = tk.Frame(anchor_widget, width=400, height=self.headerHeight, bg=BG_COLOR)
        self.headerLabel = tk.Label(self.frame, textvariable=self.header, bd=0, justify=tk.LEFT,
                                    font=self.font + (16, "bold"), width=self.labelWidth,
                                    foreground=self.hground, anchor='w', bg=self.bg)
        self.headerLabel.bind('<Button-1>', self._expand_event)

        self.labelsVars = []
        self.labels = []
        self.hovertips = []
        for _ in range(labelsCount):
            self.labelsVars.append(tk.StringVar())
            self.labels.append(tk.Label(self.frame, textvariable=self.labelsVars[-1], bd=0, justify=tk.LEFT,
                                        font=self.font + (14,), width=self.labelWidth,
                                        foreground=self.foreground, anchor='w', bg=self.bg))
            self.labels[-1].bind('<MouseWheel>', self._scroll_event)
            self.hovertips.append(MyTip(self.labels[-1], ""))
            self.hovertips[-1].hidetip()

    def pack(self, count=-1):
        if count == -1:
            count = self.labelsCount if self._expand else 0
        
        self.frame.pack()
        if self.header: self.headerLabel.pack()
        
        for i in range(min(count, self.labelsCount)):
            self.labels[i].pack()
        
        for i in range(count, self.labelsCount):
            self.labels[i].pack_forget()

    def winfo_height(self):
        height = 0
        if self.header: height += 26
        if self._expand: height += 24 * min(self.labelsCount, len(self.items)) # 24 - костыль, исправить
        return height
    
    def update(self):
        for i in range(self.labelsCount):
            if self.currItem + i < len(self.items):
                self.labelsVars[i].set(self.items[self.currItem + i])
                self.hovertips[i].hidetip()
                self.hovertips[i] = MyTip(self.labels[i], self.tips[self.currItem+i], hover_delay=100)
            else:
                self.labelsVars[i].set("")
                self.hovertips[i].hidetip()

    def append(self, label: str, tip: str = "", update: bool = False):
        self.items.append(label)
        self.tips.append(tip)
        if update: self.update()

    def _expand_event(self, event=None):
        if not self.header: return
        if self._expand: self.pack(0)
        else: self.pack(min(self.labelsCount, len(self.items)))
        self._expand = not self._expand
    
    def _scroll_event(self, event):
        self.currItem -= event.delta // 120
        maxCurr = max(len(self.items) - len(self.labels), 0)
        if self.currItem < 0: self.currItem = 0
        if self.currItem > maxCurr: self.currItem = maxCurr

        self.update()


def creat_window():
    root = tk.Tk()
    root.geometry("{}x{}+0+0".format(WIDTH, HEIGH))
    root['bg'] = BG_COLOR
    root.title("Memento_ui")
    root.resizable(False, False)
    root.overrideredirect(1)
    
    toolbar_color = "#1f262d"
    toolbar = tk.Frame(root, heigh=20, bg=toolbar_color)
    toolbar.pack(fill="x")

    def on_mouse_down(event):
        global dif_x, dif_y
        win_position = [int(coord) for coord in root.wm_geometry().split('+')[1:]]
        dif_x, dif_y = win_position[0] - event.x_root, win_position[1] - event.y_root

    def update_position(event):
        root.wm_geometry("+%d+%d" % (event.x_root + dif_x, event.y_root + dif_y))

    toolbar.bind('<ButtonPress-1>', on_mouse_down)
    toolbar.bind('<B1-Motion>', update_position)

    close = tk.Button(toolbar, text="✕", bd=0, bg=toolbar_color, foreground=TEXT_COLORS[2],
                      relief="flat", font=("Consolas", 10, "bold"), command=lambda: root.destroy())
    close.pack(anchor="e")

    return root

def main():
    root = creat_window()

    headers = ["События сегодя:", "События на следующей неделе:", "Недавно прошедшие события:"]
    scrolls = []
    for i in range(3):
        scrolls.append(ScrollList(root, 5, headers[i]))
        scrolls[-1].pack()
        scrolls[-1].update()

    def add_number(event, i):
        scrolls[i].append(f"Я понял, а вы? {len(scrolls[i].items)}", f"Подзказка {len(scrolls[i].items)}", True)
        print("add")
    
    root.bind('<e>', lambda e: add_number(e, 0))
    root.bind('<r>', lambda e: add_number(e, 1))
    root.bind('<t>', lambda e: add_number(e, 2))

if __name__ == "__main__":
    main()
