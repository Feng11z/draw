import tkinter as tk
import random
import time
import csv
import sys
import math
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

# ================= 动画粒子类 =================
class Particle:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.radius = random.randint(2, 4)
        self.life = 1.0
        self.speed = random.uniform(2, 5)
        self.angle = math.radians(random.randint(0, 360))
        self.id = canvas.create_oval(
            x - self.radius, y - self.radius,
            x + self.radius, y + self.radius,
            fill=self.random_color()
        )
        
    def random_color(self):
        return "#{:02x}{:02x}{:02x}".format(
            random.randint(200, 255),
            random.randint(0, 100),
            random.randint(0, 100)
        )
    
    def update(self):
        self.life -= 0.02
        dx = math.cos(self.angle) * self.speed
        dy = math.sin(self.angle) * self.speed
        self.canvas.move(self.id, dx, dy)
        self.canvas.itemconfig(self.id, opacity=self.life)
        return self.life > 0

# ================= 增强版圆角按钮 =================
class RoundedButton(tk.Canvas):
    def __init__(self, master=None, text="", command=None, width=100, height=40, **kwargs):
        super().__init__(master, highlightthickness=0, width=width, height=height)
        self.command = command
        self.text = text
        self.bg = kwargs.get('bg', StyleConfig.COLOR_PRIMARY)
        self.fg = kwargs.get('fg', 'white')
        self.radius = kwargs.get('radius', StyleConfig.BTN_RADIUS)
        self.particles = []
        
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
        self.spawn_particles(event.x, event.y)
        
    def _on_release(self, event):
        self.itemconfig(1, fill=self.bg)
        if self.command: 
            self.command()
            
    def spawn_particles(self, x, y):
        for _ in range(8):
            self.particles.append(Particle(self, x, y))
        self.animate_particles()
        
    def animate_particles(self):
        for p in self.particles.copy():
            if not p.update():
                self.delete(p.id)
                self.particles.remove(p)
        if self.particles:
            self.after(30, self.animate_particles)
        
    def _adjust_color(self, hex_color, factor):
        rgb = tuple(int(hex_color[i+1:i+3], 16) for i in (0, 2, 4))
        return "#{:02x}{:02x}{:02x}".format(*[min(int(c * factor), 255) for c in rgb])

# ================= 抽奖算法 =================
class LotteryAlgorithm:
    @staticmethod
    def weighted_random(prizes):
        valid_prizes = [p for p in prizes if p["quantity"] > 0]
        if not valid_prizes:
            return None
        
        total = sum(p["quantity"] for p in valid_prizes)
        rand = random.uniform(0, total)
        current = 0
        for prize in valid_prizes:
            if current + prize["quantity"] >= rand:
                return prize
            current += prize["quantity"]
        return valid_prizes[-1]

# ================= 主程序 =================
class LotteryApp:
    def __init__(self, master):
        self.master = master
        self.master.title("抽奖程序 v2.2.2")
        self.master.geometry("1000x700")
        self.animation_phase = 0
        self._init_ui()
        self._init_data()
        
    def _init_ui(self):
        self.style = ttk.Style()
        self.style.configure('TFrame', background=StyleConfig.BG_MAIN)
        
        # 主容器
        main_frame = ttk.Frame(self.master, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 奖品列表卡片
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
        
        # 动态背景画布
        self.canvas = tk.Canvas(main_frame, bg=StyleConfig.BG_MAIN, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 结果标签（放置在画布上）
        self.result_label = tk.Label(self.canvas, 
                                   text="点击开始抽奖",
                                   font=('Microsoft YaHei', 24, 'bold'),
                                   bg=StyleConfig.BG_MAIN)
        self.result_label.place(relx=0.5, rely=0.5, anchor='center')
        
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
        
        # 动画初始化
        self.animate_background()

    def animate_background(self):
        """背景流光动画"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.canvas.delete("bg_effect")
        
        # 绘制渐变条纹
        for i in range(0, 360, 15):
            angle = math.radians(i + self.animation_phase)
            x1 = width/2 + math.cos(angle) * width
            y1 = height/2 + math.sin(angle) * height
            x2 = width/2 - math.cos(angle) * width
            y2 = height/2 - math.sin(angle) * height
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=self.hsv_to_hex((i/360, 0.3, 0.95)),
                width=2,
                tags="bg_effect",
                stipple="gray50"
            )
            
        self.animation_phase = (self.animation_phase + 1) % 360
        self.master.after(50, self.animate_background)
        
    def hsv_to_hex(self, hsv):
        """HSV转十六进制颜色"""
        h, s, v = hsv
        c = v * s
        x = c * (1 - abs((h * 6) % 2 - 1))
        m = v - c
        
        if h < 1/6:
            r, g, b = c, x, 0
        elif h < 2/6:
            r, g, b = x, c, 0
        elif h < 3/6:
            r, g, b = 0, c, x
        elif h < 4/6:
            r, g, b = 0, x, c
        elif h < 5/6:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
            
        return "#{:02x}{:02x}{:02x}".format(
            int((r + m) * 255),
            int((g + m) * 255),
            int((b + m) * 255)
        )

    def _init_data(self):
        self.prizes = []
        self.is_rolling = False
        self.last_update = 0
        self.load_prizes()
        
    def load_prizes(self):
        try:
            with open("prizes.csv", "r", encoding="utf-8") as f:
                reader = csv.DictReader(filter(lambda row: row.strip() and not row.startswith('#'), f))
                
                if not reader.fieldnames or 'name' not in reader.fieldnames or 'quantity' not in reader.fieldnames:
                    raise ValueError("CSV文件必须包含name和quantity两列")
                
                self.prizes = []
                error_lines = []
                
                for line_num, row in enumerate(reader, start=2):
                    try:
                        name = row['name'].strip()
                        quantity = row['quantity'].strip()
                        
                        if not name:
                            raise ValueError("奖品名称不能为空")
                        if not quantity:
                            raise ValueError("数量不能为空")
                            
                        quantity = int(quantity)
                        if quantity < 0:
                            raise ValueError("数量不能为负数")
                            
                        self.prizes.append({"name": name, "quantity": quantity})
                    except Exception as e:
                        error_lines.append(f"第{line_num}行错误：{str(e)}")
                
                if error_lines:
                    messagebox.showwarning("数据问题", f"发现{len(error_lines)}处错误：\n" + "\n".join(error_lines[:3]))
                
                self.update_listbox()
                
        except FileNotFoundError:
            messagebox.showerror("错误", "找不到prizes.csv文件")
        except Exception as e:
            messagebox.showerror("加载失败", f"加载奖品失败：{str(e)}")
            
    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for p in self.prizes:
            self.listbox.insert(tk.END, f"{p['name']} (剩余：{p['quantity']}件)")
            
    def toggle_roll(self):
        if not self.prizes:
            messagebox.showwarning("提示", "请先加载有效奖品数据！")
            return
            
        self.is_rolling = not self.is_rolling
        
        if self.is_rolling:
            self.start_roll()
        else:
            self.stop_roll()
            
    def start_roll(self):
        valid_prizes = [p for p in self.prizes if p["quantity"] > 0]
        if not valid_prizes:
            messagebox.showwarning("提示", "所有奖品已抽完！")
            self.is_rolling = False
            return
        
        self.start_btn.config(text="停止抽奖", bg=StyleConfig.COLOR_DANGER)
        self.last_update = 0
        self.roll()
        self.start_label_animation()

    def roll(self):
        if not self.is_rolling:
            return
        
        if time.time() - self.last_update > 0.05:
            valid_prizes = [p for p in self.prizes if p["quantity"] > 0]
            if valid_prizes:
                prize = random.choice(valid_prizes)
                self.result_label.config(text=prize["name"])
                self.last_update = time.time()
        
        self.master.after(20, self.roll)
        
    def start_label_animation(self):
        """文字动画效果"""
        if not self.is_rolling:
            return
        
        # 颜色渐变
        hue = (time.time() * 0.5) % 1
        color = self.hsv_to_hex((hue, 0.8, 0.9))
        
        # 动态阴影
        shadow_offset = int(5 * math.sin(time.time() * 10))
        self.result_label.config(
            fg=color,
            bg=StyleConfig.BG_MAIN,
            relief="ridge",
            borderwidth=2,
            padx=20,
            pady=10
        )
        
        # 大小动画
        size = 24 + int(6 * math.sin(time.time() * 5))
        self.result_label.config(font=('Microsoft YaHei', size, 'bold'))
        
        self.master.after(50, self.start_label_animation)
        
    def stop_roll(self):
        if winsound: 
            try:
                winsound.MessageBeep()
            except Exception:
                pass
        
        selected = LotteryAlgorithm.weighted_random(self.prizes)
        if selected:
            selected["quantity"] -= 1
            self.update_listbox()
            self.show_final_animation(selected["name"])
        else:
            self.result_label.config(
                text="所有奖品已抽完！",
                fg=StyleConfig.COLOR_DANGER,
                font=('Microsoft YaHei', 24, 'bold')
            )
            
        self.start_btn.config(text="开始抽奖", bg=StyleConfig.COLOR_PRIMARY)
        self.is_rolling = False
        
    def show_final_animation(self, prize_name):
        """中奖最终动画"""
        self.result_label.config(
            text=f"恭喜获得：{prize_name}",
            fg=StyleConfig.COLOR_SUCCESS,
            font=('Microsoft YaHei', 32, 'bold')
        )
        
        # 粒子爆发效果
        x, y = self.result_label.winfo_x()+self.result_label.winfo_width()/2, \
               self.result_label.winfo_y()+self.result_label.winfo_height()/2
        
        for _ in range(50):
            Particle(self.canvas, x, y)
            
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
