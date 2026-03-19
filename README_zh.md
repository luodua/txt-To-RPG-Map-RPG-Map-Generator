# Txt To RPG Map

[English](./README_en.md) | 中文

一个用于生成 RPG 游戏地图的工具，支持室外场景和室内场景的地图渲染。

## 效果展示

![室外地图示例](output/output_map.png)

![调试输出](output/debug_output.png)

![调试输出2](output/debug_output2.png)

## 项目特点

本项目专为 RPG 游戏开发者设计，核心优势在于：

**AI 快速生成**：只需用自然语言描述你想要的地图场景，配合内置的提示词模板，大模型即可生成完整的 JSON 地图配置。无需手动排列图块，一键渲染即可得到 RPG Maker 风格的像素地图。

**零门槛操作**：只需 Pillow 一个依赖库，无需配置数据库或复杂的开发环境。提供图形界面工具辅助素材处理，小白也能快速上手。

**灵活的图层系统**：支持程序化生成（矩形、圆形、直线）和手动放置两种方式，可精确控制每个物体的位置和层级关系。

**开箱即用**：内置室外和室内两组素材库，涵盖常见的 RPG 场景元素，包括地形、建筑、装饰物等。

**高度可扩展**：支持自定义素材，只需将 PNG 图片放入对应目录即可添加新图块。自动识别单格和多格物体。

## 项目结构

```
mapgenerater/
├── assets/                    # 素材资源
│   ├── tiles/                # 室外地图素材
│   │   ├── grass.png         # 草地 (1x1)
│   │   ├── tree.png           # 大树 (4x5)
│   │   ├── house.png          # 房屋 (5x6)
│   │   ├── road.png           # 道路 (1x1)
│   │   ├── flower.png         # 花朵 (1x1)
│   │   ├── wood.png           # 木头 (1x3)
│   │   ├── wood2.png          # 小木头 (1x1)
│   │   ├── wood3.png          # 树桩 (1x1)
│   │   ├── Mushroom.png       # 蘑菇 (1x1)
│   │   └── Street lamp.png    # 路灯 (1x3)
│   └── insidetiles/          # 室内地图素材
│       ├── 室内地板.png       # 室内地板 (1x1)
│       ├── 室内墙.png         # 墙壁 (1x1)
│       ├── 室内床.png         # 床 (2x3)
│       ├── 室内桌子.png       # 桌子 (2x2)
│       └── ...
├── examples/                  # 示例文件
│   ├── map_layout.json        # 室外地图配置示例
│   ├── indoor_template.json   # 室内地图配置示例
│   ├── indoor_map.json        # 室内地图示例
│   └── test_floor.json        # 测试配置
├── tools/                     # 工具脚本
│   ├── map_renderer.py        # 地图渲染器 (核心)
│   ├── tile_selector.py       # 图块选择器 GUI
│   ├── tile_annotator.py      # 多格物体标注工具
│   └── analyze_tiles.py       # 素材分析工具
├── prompts/                   # AI 提示词
│   ├── 提示词.txt             # 室外地图生成提示词
│   └── 室内提示词.txt         # 室内地图生成提示词
├── docs/                      # 文档
│   ├── tiles_list.txt         # 室外素材列表
│   ├── insidetiles_list.txt   # 室内素材列表
│   └── tile_selector_readme.txt
├── output/                    # 输出目录
│   └── output_map.png         # 渲染结果
└── README.md                  # 中文说明
```

## 安装

### 依赖

```bash
pip install Pillow
```

Pillow 是唯一的外部依赖，用于图像处理。

## 使用方法

### 1. 地图渲染器 (核心工具)

渲染 JSON 配置文件生成地图图片：

```bash
# 默认渲染
python tools/map_renderer.py

# 指定配置文件
python tools/map_renderer.py examples/map_layout.json

# 指定素材目录
python tools/map_renderer.py -t assets/tiles
```

输出文件：`output/output_map.png`

### 2. 图块选择器

图形界面的图块裁剪工具，用于从大图中选取单个图块：

```bash
python tools/tile_selector.py
```

功能：
- 打开图片文件
- 拖动选择区域
- 导出选中区域为单独的图片

### 3. 多格物体标注工具

用于标注多格物体的位置和大小：

```bash
python tools/tile_annotator.py
# 需要传入图片路径，例如：
# python tools/tile_annotator.py "path/to/tileset.png"
```

功能：
- 显示网格线
- 框选多格物体区域
- 保存标注配置

### 4. 素材分析工具

分析素材目录中的图片规格：

```bash
# 分析室内素材
python tools/analyze_tiles.py assets/insidetiles

# 分析室外素材
python tools/analyze_tiles.py assets/tiles
```

## JSON 配置格式

### 基础结构

```json
{
  "mapName": "地图名称",
  "tileSize": 32,
  "width": 20,
  "height": 15,
  "defaultTile": "grass",
  "layers": [...]
}
```

### 图层类型

1. **procedural**: 程序化生成
   - `rectangle`: 矩形区域
   - `circle`: 圆形区域
   - `line`: 直线

2. **grid**: 完整二维数组

3. **sparse**: 稀疏数组，只列出物体位置

### 示例

```json
{
  "layers": [
    {
      "name": "地面层",
      "type": "procedural",
      "rules": [
        {"type": "rectangle", "tile": "road", "x1": 5, "y1": 4, "x2": 14, "y2": 10}
      ]
    },
    {
      "name": "物体层",
      "type": "sparse",
      "data": [
        {"tile": "house", "x": 3, "y": 3},
        {"tile": "tree", "x": 2, "y": 2}
      ]
    }
  ]
}
```

## AI 辅助生成

使用 `prompts/` 目录下的提示词文件，配合 AI 生成地图布局 JSON：

1. 复制提示词给 AI
2. 描述你想要的地图
3. AI 生成 JSON 配置
4. 保存为 JSON 文件
5. 使用渲染器生成地图

## 素材规格

- 图块大小：32x32 像素
- 支持格式：PNG, JPG, BMP
- 多格物体：根据图片尺寸自动计算格子数

## 许可证

MIT License
