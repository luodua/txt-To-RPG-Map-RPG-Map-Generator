# 图块选择器使用说明

## 启动方式

```bash
# 方式1: 直接指定图片
python tile_selector.py 图片路径

# 方式2: 运行后选择图片
python tile_selector.py
```

## 使用方法

1. 打开图片后，点击选择需要的 32x32 区域
2. 选中的区域会显示红色边框
3. 再次点击已选中的区域可以取消选择
4. 点击"导出选中区域"选择保存目录
5. 导出的文件命名为 tile_x_y.png

## 示例

```bash
# 选择裁剪好的素材图片
python tile_selector.py 009-CastleTown01复刻/009-CastleTown01复刻_1_1.png
```
