import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os

class TileSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("地图图块选择器")
        
        self.tile_size = 32
        self.image_path = None
        self.original_image = None
        self.start_pos = None
        self.current_pos = None
        self.selected_regions = []
        
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=5)
        
        tk.Button(top_frame, text="打开图片", command=self.open_image).pack(side=tk.LEFT, padx=5)
        
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='gray')
        self.canvas.pack()
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="导出选中区域", command=self.export_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="清空选择", command=self.clear_selection).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="继续选择", command=self.continue_selection).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="退出", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)
        
        self.info_label = tk.Label(info_frame, text="请先打开图片")
        self.info_label.pack()
        
        self.size_label = tk.Label(info_frame, text="")
        self.size_label.pack()
        
        self.scale = 1
        self.display_image = None
        self.tk_image = None
        
        self.root.mainloop()
    
    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[("图片文件", "*.png *.bmp *.jpg"), ("所有文件", "*.*")]
        )
        if not file_path:
            return
        
        self.image_path = file_path
        self.original_image = Image.open(file_path)
        self.image_width, self.image_height = self.original_image.size
        
        self.cols = self.image_width // self.tile_size
        self.rows = self.image_height // self.tile_size
        
        canvas_width = min(900, self.image_width)
        canvas_height = min(700, self.image_height)
        
        self.canvas.config(width=canvas_width, height=canvas_height)
        
        scale = min(canvas_width / self.image_width, canvas_height / self.image_height)
        new_w = int(self.image_width * scale)
        new_h = int(self.image_height * scale)
        self.display_image = self.original_image.resize((new_w, new_h))
        self.scale = scale
        
        self.tk_image = ImageTk.PhotoImage(self.display_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        
        self.selected_regions = []
        self.info_label.config(text=f"已打开: {os.path.basename(file_path)} ({self.cols}x{self.rows}格)")
        self.size_label.config(text="拖动选择区域")
    
    def on_click(self, event):
        if not self.original_image:
            return
        
        x = int(event.x / self.scale)
        y = int(event.y / self.scale)
        
        col = min(x // self.tile_size, self.cols - 1)
        row = min(y // self.tile_size, self.rows - 1)
        
        self.start_pos = (col, row)
        self.current_pos = (col, row)
    
    def on_drag(self, event):
        if not self.start_pos or not self.original_image:
            return
        
        x = int(event.x / self.scale)
        y = int(event.y / self.scale)
        
        col = min(max(x // self.tile_size, 0), self.cols - 1)
        row = min(max(y // self.tile_size, 0), self.rows - 1)
        
        self.current_pos = (col, row)
        self.draw_preview()
    
    def on_release(self, event):
        if not self.start_pos or not self.current_pos or not self.original_image:
            return
        
        x1, y1 = self.start_pos
        x2, y2 = self.current_pos
        
        min_x = min(x1, x2)
        max_x = max(x1, x2)
        min_y = min(y1, y2)
        max_y = max(y1, y2)
        
        region = {
            'x1': min_x,
            'y1': min_y,
            'x2': max_x + 1,
            'y2': max_y + 1,
            'width': max_x - min_x + 1,
            'height': max_y - min_y + 1
        }
        
        if region not in self.selected_regions:
            self.selected_regions.append(region)
        
        self.start_pos = None
        self.current_pos = None
        self.redraw_all()
        self.info_label.config(text=f"已选择: {len(self.selected_regions)} 个区域")
    
    def draw_preview(self):
        if not self.start_pos or not self.current_pos:
            return
        
        self.canvas.delete("preview")
        
        x1, y1 = self.start_pos
        x2, y2 = self.current_pos
        
        min_x = min(x1, x2)
        max_x = max(x1, x2)
        min_y = min(y1, y2)
        max_y = max(y1, y2)
        
        px1 = min_x * self.tile_size * self.scale
        py1 = min_y * self.tile_size * self.scale
        px2 = (max_x + 1) * self.tile_size * self.scale
        py2 = (max_y + 1) * self.tile_size * self.scale
        
        self.canvas.create_rectangle(px1, py1, px2, py2, outline='yellow', width=3, tags="preview")
        
        w = max_x - min_x + 1
        h = max_y - min_y + 1
        self.size_label.config(text=f"当前选择: {w}x{h}")
    
    def redraw_all(self):
        self.canvas.delete("region")
        
        for region in self.selected_regions:
            px1 = region['x1'] * self.tile_size * self.scale
            py1 = region['y1'] * self.tile_size * self.scale
            px2 = region['x2'] * self.tile_size * self.scale
            py2 = region['y2'] * self.tile_size * self.scale
            
            self.canvas.create_rectangle(px1, py1, px2, py2, outline='red', width=3, tags="region")
        
        if self.selected_regions:
            r = self.selected_regions[-1]
            self.size_label.config(text=f"当前选择: {r['width']}x{r['height']}")
    
    def clear_selection(self):
        self.selected_regions = []
        self.start_pos = None
        self.current_pos = None
        self.canvas.delete("region")
        self.canvas.delete("preview")
        self.info_label.config(text="已清空选择")
        self.size_label.config(text="")
    
    def continue_selection(self):
        self.start_pos = None
        self.current_pos = None
        self.canvas.delete("preview")
        self.size_label.config(text="继续选择区域")
    
    def export_selected(self):
        if not self.selected_regions:
            messagebox.showwarning("警告", "请先选择至少一个区域")
            return
        
        export_dir = filedialog.askdirectory(title="选择导出目录")
        if not export_dir:
            return
        
        base_name = os.path.splitext(os.path.basename(self.image_path))[0]
        
        for i, region in enumerate(self.selected_regions):
            left = region['x1'] * self.tile_size
            top = region['y1'] * self.tile_size
            right = region['x2'] * self.tile_size
            bottom = region['y2'] * self.tile_size
            
            tile = self.original_image.crop((left, top, right, bottom))
            
            w = region['width']
            h = region['height']
            
            default_name = f"{base_name}_{w}x{h}_{i+1}"
            filename = simpledialog.askstring("文件名", f"请输入第 {i+1} 个区域的文件名:", initialvalue=default_name)
            if not filename:
                continue
            if not filename.endswith('.png'):
                filename += '.png'
            
            tile.save(os.path.join(export_dir, filename))
        
        messagebox.showinfo("完成", f"已导出 {len(self.selected_regions)} 个区域到:\n{export_dir}")

if __name__ == "__main__":
    TileSelector()
