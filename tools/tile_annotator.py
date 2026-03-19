import json
import tkinter as tk
from PIL import Image, ImageTk

class TileAnnotator:
    """图块标注工具，用鼠标框选多格物体"""
    
    def __init__(self, tileset_path, tile_size=32):
        self.tile_size = tile_size
        self.multi_tiles = []
        
        # 加载图片
        self.img = Image.open(tileset_path)
        self.tk_img = ImageTk.PhotoImage(self.img)
        
        # 创建窗口
        self.root = tk.Tk()
        self.root.title("多格物体标注工具")
        
        # 画布
        self.canvas = tk.Canvas(self.root, width=self.img.width, height=self.img.height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        
        # 绘制网格线
        self.draw_grid()
        
        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # 保存按钮
        tk.Button(self.root, text="保存配置", command=self.save_config).pack()
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        
        self.root.mainloop()
    
    def draw_grid(self):
        """绘制网格线"""
        for x in range(0, self.img.width, self.tile_size):
            self.canvas.create_line(x, 0, x, self.img.height, fill="red", width=1)
        for y in range(0, self.img.height, self.tile_size):
            self.canvas.create_line(0, y, self.img.width, y, fill="red", width=1)
    
    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
    
    def on_drag(self, event):
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline="blue", width=2
        )
    
    def on_release(self, event):
        # 计算网格坐标
        x1 = min(self.start_x, event.x) // self.tile_size
        y1 = min(self.start_y, event.y) // self.tile_size
        x2 = max(self.start_x, event.x) // self.tile_size
        y2 = max(self.start_y, event.y) // self.tile_size
        
        width = x2 - x1 + 1
        height = y2 - y1 + 1
        
        # 弹出输入框让用户输入名称
        dialog = tk.Toplevel(self.root)
        tk.Label(dialog, text=f"为这个{width}x{height}的物体命名：").pack()
        entry = tk.Entry(dialog)
        entry.pack()
        
        def confirm():
            name = entry.get()
            self.multi_tiles.append({
                "name": name,
                "x": x1,
                "y": y1,
                "width": width,
                "height": height
            })
            # 用绿色框标记已标注的区域
            self.canvas.create_rectangle(
                x1 * self.tile_size, y1 * self.tile_size,
                (x2 + 1) * self.tile_size, (y2 + 1) * self.tile_size,
                outline="green", width=3
            )
            dialog.destroy()
        
        tk.Button(dialog, text="确认", command=confirm).pack()
    
    def save_config(self):
        with open("slice_config.json", "w") as f:
            json.dump({"multi_tiles": self.multi_tiles}, f, indent=2)
        print("配置已保存到 slice_config.json")
        self.root.destroy()

# 使用
# TileAnnotator("TileA.png", 32)