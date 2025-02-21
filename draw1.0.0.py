import tkinter as tk
import random
from tkinter import messagebox

class LotteryApp:
    def __init__(self, master):
        self.master = master
        self.master.title("抽奖程序")
        self.master.geometry("500x400")
        
        # 初始化变量
        self.prizes = []
        self.prize_pool = []
        self.is_rolling = False
        
        # 创建界面元素
        self.create_widgets()
        
        # 自动加载奖品
        self.load_prizes()

    def create_widgets(self):
        # 网站链接
        self.site_label = tk.Label(self.master, text="lanyu-cn.cn", 
                                 fg="blue", cursor="hand2")
        self.site_label.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)

        # 奖品列表显示
        self.listbox = tk.Listbox(self.master, width=40, height=10)
        self.listbox.pack(pady=10)
        
        # 信息标签
        self.info_label = tk.Label(self.master, text="点击开始进行抽奖")
        self.info_label.pack(pady=5)
        
        # 结果显示
        self.result_label = tk.Label(self.master, text="", 
                                    font=('Helvetica', 18), fg='red')
        self.result_label.pack(pady=10)
        
        # 开始按钮
        self.start_btn = tk.Button(self.master, text="开始", 
                                 command=self.start_rolling, width=10)
        self.start_btn.pack(pady=5)

    def load_prizes(self):
        try:
            with open("prizes.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            self.prizes = []
            self.prize_pool = []
            
            for line in lines:
                line = line.strip()
                if line and "," in line:
                    name, quantity = line.split(",", 1)
                    quantity = int(quantity.strip())
                    self.prizes.append((name.strip(), quantity))
                    self.prize_pool.extend([name.strip()] * quantity)
            
            random.shuffle(self.prize_pool)
            self.update_listbox()
            
            if not self.prizes:
                messagebox.showwarning("警告", "奖品列表为空！")
                
        except FileNotFoundError:
            messagebox.showerror("错误", "未找到prizes.txt文件！")
        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败：{str(e)}")

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for name, qty in self.prizes:
            self.listbox.insert(tk.END, f"{name} (剩余: {qty}份)")

    def start_rolling(self):
        if not self.prize_pool:
            messagebox.showinfo("提示", "所有奖品已抽完！")
            return
            
        self.is_rolling = True
        self.start_btn.config(state=tk.DISABLED)
        self.roll()
        # 设置3秒后自动停止
        self.master.after(3000, self.stop_rolling)

    def roll(self):
        if self.is_rolling and self.prize_pool:
            current_prize = random.choice(self.prize_pool)
            self.result_label.config(text=current_prize)
            self.master.after(100, self.roll)

    def stop_rolling(self):
        self.is_rolling = False
        self.start_btn.config(state=tk.NORMAL)
        
        if self.prize_pool:
            selected_prize = self.result_label.cget("text")
            if selected_prize in self.prize_pool:
                self.prize_pool.remove(selected_prize)
                for i, (name, qty) in enumerate(self.prizes):
                    if name == selected_prize:
                        self.prizes[i] = (name, qty-1)
                        break
                self.update_listbox()
                messagebox.showinfo("中奖结果", f"恭喜抽中：{selected_prize}！")
        else:
            self.result_label.config(text="")
            messagebox.showinfo("提示", "所有奖品已抽完！")

if __name__ == "__main__":
    root = tk.Tk()
    app = LotteryApp(root)
    root.mainloop()