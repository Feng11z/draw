import tkinter as tk
import random
from tkinter import messagebox
from tkinter import ttk

class RoundedButton(tk.Canvas):
    def __init__(self, master=None, text="", radius=25, bg="#3498db", fg="white", 
                 command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.command = command
        self.bg = bg
        self.fg = fg
        self.radius = radius
        
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        
        self.id = None
        self.text_id = None
        self.draw()
        
    def draw(self):
        self.delete("all")
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        
        self.id = self.create_round_rect(
            0, 0, width, height, 
            radius=self.radius, 
            fill=self.bg,
            outline=self.bg
        )
        self.text_id = self.create_text(
            width/2, height/2,
            text=self["text"],
            fill=self.fg,
            font=('Microsoft YaHei', 12, 'bold')
        )
        
    def create_round_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def _on_press(self, event):
        self.itemconfig(self.id, fill=self._lighter_color(self.bg, 0.8))
        
    def _on_release(self, event):
        self.itemconfig(self.id, fill=self.bg)
        if self.command:
            self.command()
            
    def _lighter_color(self, hex_color, factor=0.8):
        rgb = tuple(int(hex_color[i+1:i+3], 16) for i in (0, 2, 4))
        lighter = tuple(min(int(c * factor) + 50, 255) for c in rgb)
        return "#%02x%02x%02x" % lighter

class LotteryApp:
    def __init__(self, master):
        self.master = master
        self.master.title("抽奖程序 v1.1")
        self.master.geometry("600x480")
        self.master.configure(bg="#f0f3f5")
        
        # 初始化变量
        self.prizes = []
        self.prize_pool = []
        self.is_rolling = False
        
        style = ttk.Style()
        style.configure("TListbox", font=('Microsoft YaHei', 10), 
                       background="#ffffff", relief="flat")
        
        # 创建界面元素
        self.create_widgets()
        self.load_prizes()

    def create_widgets(self):
        # 主容器
        main_frame = tk.Frame(self.master, bg="#f0f3f5")
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # 网站链接
        self.site_label = tk.Label(main_frame, text="lanyu-cn.cn", 
                                 fg="#3498db", cursor="hand2",
                                 font=('Microsoft YaHei', 10, 'underline'),
                                 bg="#f0f3f5")
        self.site_label.pack(side=tk.BOTTOM, anchor=tk.SE, pady=10)
        
        # 奖品列表容器
        list_frame = tk.Frame(main_frame, bg="#ffffff", bd=0,
                            highlightthickness=2, 
                            highlightbackground="#e0e5ec")
        list_frame.pack(pady=15, fill=tk.BOTH, expand=True)
        
        # 奖品列表标题
        tk.Label(list_frame, text="奖品库存", font=('Microsoft YaHei', 12, 'bold'),
                bg="#ffffff").pack(pady=5)
        
        # 奖品列表显示
        self.listbox = tk.Listbox(list_frame, width=40, height=8,
                                 font=('Microsoft YaHei', 10),
                                 bg="#ffffff", bd=0,
                                 highlightthickness=0)
        self.listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        
        # 结果显示区
        result_frame = tk.Frame(main_frame, bg="#ffffff", bd=0,
                               highlightthickness=2,
                               highlightbackground="#e0e5ec")
        result_frame.pack(pady=15, fill=tk.X)
        
        self.result_label = tk.Label(result_frame, text="点击开始抽奖", 
                                   font=('Microsoft YaHei', 24, 'bold'),
                                   fg="#e74c3c", bg="#ffffff")
        self.result_label.pack(pady=20)
        
        # 开始按钮
        self.start_btn = RoundedButton(main_frame, text="开始抽奖", 
                                      radius=30, bg="#3498db", 
                                      width=200, height=50,
                                      command=self.start_rolling)
        self.start_btn.pack(pady=10)

    def load_prizes(self):
        # ...（保持原有load_prizes方法不变）...

    def update_listbox(self):
        # ...（保持原有update_listbox方法不变）...

    def start_rolling(self):
        # ...（保持原有start_rolling方法不变）...

    def roll(self):
        # ...（保持原有roll方法不变）...

    def stop_rolling(self):
        # ...（保持原有stop_rolling方法不变）...

if __name__ == "__main__":
    root = tk.Tk()
    app = LotteryApp(root)
    root.mainloop()
