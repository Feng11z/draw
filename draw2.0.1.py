import tkinter as tk
import random
import time
import csv
import sys
from tkinter import ttk, messagebox
try:
    import winsound
except ImportError:
    winsound = None

# ================= 样式配置 =================
class StyleConfig:
    FONT_TITLE = ('Microsoft YaHei', 14, 'bold')
    FONT_TEXT = ('Microsoft YaHei', 11)
    COLOR_PRIMARY = "#3498db"
    COLOR_DANGER = "#e74c3c"
    COLOR_SUCCESS = "#2ecc71"
    BG_MAIN = "#f0f3f5"
    BG_CARD = "#ffffff"
    BORDER_COLOR = "#e0e5ec"
    BTN_RADIUS = 25

# ================= 圆角按钮控件 =================
class RoundedButton(tk.Canvas):
    def __init__(self, master=None, text="", command=None, width=100, height=40, **kwargs):
        super().__init__(master, highlightthickness=0, width=width, height=height)
        self.command = command
        self.text = text
        self.bg = kwargs.get('bg', StyleConfig.COLOR_PRIMARY)
        self.fg = kwargs.get('fg', 'white')
        self.radius = kwargs.get('radius', StyleConfig.BTN_RADIUS)
        
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.draw()
        
    def draw(self):
        self.delete("all")
        width, height = self.winfo_reqwidth(), self.winfo_reqheight()
        self.create_round_rect(0, 0, width, height, self.radius, fill=self.bg, outline=self.bg)
        self.create_text(width/2, height/2, text=self.text, fill=self.fg, font=StyleConfig.FONT_TEXT)
        
    def create_round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1,
                  x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2,
                  x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2,
                  x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
        return self.create_polygon(points, **kwargs, smooth=True)

    def _on_press(self, event):
        self.itemconfig(1, fill=self._adjust_color(self.bg, 0.8))
        
    def _on_release(self, event):
        self.itemconfig(1, fill=self.bg)
        if self.command: self.command()
        
    def _adjust_color(self, hex_color, factor):
        rgb = tuple(int(hex_color[i+1:i+3], 16) for i in (0, 2, 4))
        return "#{:02x}{:02x}{:02x}".format(*[min(int(c * factor), 255) for c in rgb])

# ================= 抽奖算法 =================
class LotteryAlgorithm:
    @staticmethod
    def weighted_random(prizes):
        total = sum(p["quantity"] for p in prizes)
        rand = random.uniform(0, total)
        current = 0
        for prize in prizes:
            if current + prize["quantity"] >= rand:
                return prize
            current += prize["quantity"]
        return prizes[-1]

# ================= 主程序 =================
class LotteryApp:
    def __init__(self, master):
        self.master = master
        self.master.title("抽奖程序 v2.0")
        self.master.geometry("800x600")
        self._init_ui()
        self._init_data()
        
    def _init_ui(self):
        self.style = ttk.Style()
        self.style.configure('TFrame', background=StyleConfig.BG_MAIN)
        
        main_frame = ttk.Frame(self.master, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 奖品列表
        list_card = ttk.Frame(main_frame, style='TFrame', relief='solid', borderwidth=2)
        list_card.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(list_card, text="奖品库存", font=StyleConfig.FONT_TITLE, background=StyleConfig.BG_CARD).pack(pady=5)
        
        scrollbar = ttk.Scrollbar(list_card)
        self.listbox = tk.Listbox(list_card, yscrollcommand=scrollbar.set,
                                font=StyleConfig.FONT_TEXT,
                                bg=StyleConfig.BG_CARD,
                                highlightthickness=0)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 结果显示
        result_frame = ttk.Frame(main_frame, style='TFrame', relief='solid', borderwidth=2)
        result_frame.pack(fill=tk.X, pady=10)
        
        self.result_label = ttk.Label(result_frame, 
                                    text="点击开始抽奖",
                                    font=('Microsoft YaHei', 24, 'bold'),
                                    foreground=StyleConfig.COLOR_DANGER,
                                    background=StyleConfig.BG_CARD)
        self.result_label.pack(pady=20)
        
        # 按钮区
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        self.start_btn = RoundedButton(btn_frame, text="开始抽奖", 
                                      width=200, height=50,
                                      bg=StyleConfig.COLOR_PRIMARY,
                                      command=self.toggle_roll)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(btn_frame, text="中奖记录", command=self.show_history).pack(side=tk.LEFT)
        
        # 底部信息
        ttk.Label(main_frame, text="技术支持: lanyu-cn.cn", cursor="hand2").pack(side=tk.BOTTOM)
        self.master.bind("<Configure>", self.on_resize)
        
    def _init_data(self):
        self.prizes = []
        self.is_rolling = False
        self.last_update = 0
        self.load_prizes()
        
    def on_resize(self, event):
        new_width = max(400, self.master.winfo_width() - 40)
        self.listbox.config(width=new_width//20)
        
    def load_prizes(self):
        try:
            with open("prizes.csv", "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.prizes = [{"name": row["name"], "quantity": int(row["quantity"])} for row in reader]
            self.update_listbox()
        except Exception as e:
            messagebox.showerror("错误", f"加载奖品失败：{str(e)}")
            
    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for p in self.prizes:
            self.listbox.insert(tk.END, f"{p['name']} (剩余：{p['quantity']}件)")
            
    def toggle_roll(self):
        if not self.prizes:
            messagebox.showwarning("提示", "请先加载奖品数据！")
            return
            
        self.is_rolling = not self.is_rolling
        if self.is_rolling:
            self.start_roll()
        else:
            self.stop_roll()
            
    def start_roll(self):
        self.start_btn.config(text="停止抽奖", bg=StyleConfig.COLOR_DANGER)
        self.result_label.config(fg=StyleConfig.COLOR_DANGER)
        self.roll()
        
    def stop_roll(self):
        if winsound: winsound.MessageBeep()
        self.start_btn.config(text="开始抽奖", bg=StyleConfig.COLOR_PRIMARY)
        selected = LotteryAlgorithm.weighted_random(self.prizes)
        self.result_label.config(text=selected["name"], fg=StyleConfig.COLOR_SUCCESS)
        self.is_rolling = False
        
    def roll(self):
        if self.is_rolling and time.time() - self.last_update > 0.05:
            prize = random.choice(self.prizes)
            self.result_label.config(
                text=prize["name"],
                fg="#{:06x}".format(random.randint(0, 0xFFFFFF))
            )
            self.last_update = time.time()
        if self.is_rolling:
            self.master.after(20, self.roll)
            
    def show_history(self):
        history_win = tk.Toplevel(self.master)
        history_win.title("中奖记录")
        tree = ttk.Treeview(history_win, columns=("time", "prize"), show="headings")
        tree.heading("time", text="时间")
        tree.heading("prize", text="奖品")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for i in range(50):
            tree.insert("", "end", values=(time.strftime("%Y-%m-%d %H:%M"), f"奖品{i+1}"))

if __name__ == "__main__":
    if sys.platform == "win32":
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()
    app = LotteryApp(root)
    root.mainloop()
