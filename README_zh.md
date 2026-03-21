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

---

# 技术文档

## 1. 问题定义：我们要解决什么？现有方案哪里不好？

### 核心问题
RPG游戏地图制作是一个耗时且技术门槛高的过程。传统方案存在以下问题：

**现有方案痛点：**
1. **手动布局效率低下**：传统地图编辑器需要逐格放置图块，制作20x15的地图需要手动放置300个图块
2. **学习曲线陡峭**：专业地图编辑器（如Tiled、RPG Maker）需要学习复杂界面和操作
3. **AI集成困难**：现有工具无法直接利用AI生成地图布局，需要人工转换
4. **资产管理复杂**：多图块对象（如房屋、树木）需要手动计算尺寸和位置
5. **缺乏程序化生成**：难以批量生成相似风格的地图变体

### 我们的解决方案
Txt To RPG Map 通过以下方式解决上述问题：
- **自然语言描述** → **AI生成JSON** → **自动渲染地图**
- 简化工作流：从数小时的手动布局减少到几分钟的AI辅助生成
- 零配置依赖：仅需Pillow库，无需数据库或复杂环境
- 智能资产识别：自动检测图块尺寸，支持多图块对象

## 2. 架构总览：系统如何组织？画图+文字

### 系统架构图
```
┌─────────────────────────────────────────────────────────────┐
│                   用户输入层 (User Input)                    │
├─────────────────────────────────────────────────────────────┤
│ 1. 自然语言描述  │ 2. JSON配置文件  │ 3. 图形界面工具          │
│   "森林村庄"     │   map_layout.json │   tile_selector.py     │
└─────────────────┴───────────────────┴───────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   核心处理层 (Core Processing)                │
├─────────────────────────────────────────────────────────────┤
│  map_renderer.py ──┐                                         │
│  • 配置解析        │                                         │
│  • 图层合成        ├──▶ 渲染引擎                             │
│  • 碰撞检测        │    • 程序化生成 (矩形/圆形/直线)        │
│  • 多图块处理      │    • 稀疏数组优化                       │
│                    │    • 图层叠加算法                       │
│  analyze_tiles.py ─┘                                         │
│  • 资产分析        │                                         │
│  • 尺寸检测        │                                         │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   资产管理层 (Asset Management)               │
├─────────────────────────────────────────────────────────────┤
│  assets/                    │  tools/                       │
│  ├── tiles/       (户外)    │  ├── tile_annotator.py        │
│  │   ├── grass.png          │  │   • 多图块标注             │
│  │   ├── tree.png (4x5)     │  │   • 网格显示              │
│  │   └── ...                │  │                           │
│  └── insidetiles/ (室内)    │  └── tile_selector.py        │
│      ├── 室内墙.png         │      • 图块选择器            │
│      ├── 室内床.png (2x3)   │      • 区域裁剪              │
│      └── ...                │                               │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   输出层 (Output)                            │
├─────────────────────────────────────────────────────────────┤
│  output/output_map.png      │  docs/                        │
│  • PNG格式地图              │  • tiles_list.txt            │
│  • 透明通道支持             │  • 资产文档                  │
│  • 分层渲染结果             │                               │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件说明

**1. 渲染引擎 (map_renderer.py)**
- 配置驱动：基于JSON配置文件生成地图
- 图层系统：支持ground/object/decorative多层叠加
- 程序化生成：矩形、圆形、直线等基本图形
- 碰撞检测：防止对象重叠（可配置）

**2. 资产管理系统**
- 自动尺寸检测：根据图像像素计算图块尺寸
- 别名映射：支持英文名到中文文件名的映射
- 多图块支持：自动处理4x5树木、5x6房屋等大型对象

**3. 辅助工具集**
- 图块选择器：从大图中裁剪单个图块
- 图块标注器：标注多图块对象的尺寸和位置
- 资产分析器：分析目录中所有图块的规格

## 3. 核心创新：我们独特的设计是什么？伪代码/流程图

### 创新点1：AI友好的JSON配置格式
```json
{
  "mapName": "森林村庄",
  "tileSize": 32,
  "width": 20,
  "height": 15,
  "defaultTile": "grass",
  "layers": [
    {
      "name": "地面层",
      "type": "procedural",
      "rules": [
        {
          "type": "rectangle", 
          "tile": "road", 
          "x1": 5, "y1": 4, "x2": 14, "y2": 10
        }
      ]
    }
  ]
}
```

### 创新点2：智能图层合成算法
```python
# 伪代码：地图渲染核心算法
def render_map(config, tileset):
    # 1. 创建画布
    canvas = create_canvas(config.width, config.height)
    
    # 2. 按顺序渲染每个图层
    for layer in config.layers:
        if layer.type == "procedural":
            render_procedural_layer(canvas, layer, tileset)
        elif layer.type == "grid":
            render_grid_layer(canvas, layer, tileset)
        elif layer.type == "sparse":
            render_sparse_layer(canvas, layer, tileset)
    
    # 3. 应用碰撞检测（可选）
    if config.enable_collision:
        apply_collision_detection(canvas)
    
    return canvas

# 程序化图层渲染
def render_procedural_layer(canvas, layer, tileset):
    for rule in layer.rules:
        if rule.type == "rectangle":
            fill_rectangle(canvas, rule, tileset[rule.tile])
        elif rule.type == "circle":
            fill_circle(canvas, rule, tileset[rule.tile])
        elif rule.type == "line":
            draw_line(canvas, rule, tileset[rule.tile])
```

### 创新点3：多图块对象自动处理
```
流程图：多图块对象渲染流程
开始
  ↓
读取图像 → 计算尺寸 (width/height/tile_size)
  ↓
判断图块类型:
  • 单图块 (1x1) → 直接存储
  • 多图块 (NxM) → 记录尺寸信息
  ↓
渲染时处理:
  if 多图块对象:
      for dy in range(对象高度):
          for dx in range(对象宽度):
              计算子图块位置 (x+dx, y+dy)
              渲染子图块
  else:
      直接渲染单图块
  ↓
结束
```

### 创新点4：零配置资产扩展
```python
# 资产自动发现机制
def discover_assets(asset_dir):
    assets = {}
    for file in os.listdir(asset_dir):
        if is_image_file(file):
            name = remove_extension(file)
            img = load_image(file)
            size = calculate_tile_size(img)  # 自动计算: 32x32=1x1, 128x160=4x5
            assets[name] = {
                "image": img,
                "width": size[0],  # 图块宽度
                "height": size[1], # 图块高度
                "is_multi": size[0] > 1 or size[1] > 1
            }
    return assets
```






