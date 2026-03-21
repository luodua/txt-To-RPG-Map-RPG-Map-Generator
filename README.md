# Txt To RPG Map

[English](./README.md) | [中文](./README_zh.md)

A tool for generating RPG game maps, supporting both outdoor and indoor scene rendering.

## Preview

![Outdoor Map Example](output/output_map.png)

![Debug Output](output/debug_output.png)

![Debug Output 2](output/debug_output2.png)

## Key Features

This project is designed for RPG game developers with these core advantages:

**AI-Assisted Generation**: Simply describe your desired map scene in natural language, and with the built-in prompt templates, LLMs can generate complete JSON map configurations instantly. No need to manually arrange tiles - one-click rendering gives you RPG Maker-style pixel maps.

**Zero Learning Curve**: Only requires Pillow as a dependency. No database configuration or complex development environment needed. GUI tools provided for asset processing, making it easy for beginners.

**Flexible Layer System**: Supports both procedural generation (rectangles, circles, lines) and manual placement. Precise control over each object's position and layer hierarchy.

**Ready to Use**: Built-in outdoor and indoor asset libraries covering common RPG scene elements including terrain, buildings, and decorations.

**Highly Extensible**: Supports custom assets - just drop PNG images into the corresponding directory to add new tiles. Automatically detects single-tile and multi-tile objects.

## Project Structure

```
mapgenerater/
├── assets/                    # Asset resources
│   ├── tiles/                # Outdoor map tiles
│   │   ├── grass.png         # Grass (1x1)
│   │   ├── tree.png           # Tree (4x5)
│   │   ├── house.png          # House (5x6)
│   │   ├── road.png           # Road (1x1)
│   │   ├── flower.png         # Flower (1x1)
│   │   ├── wood.png           # Wood (1x3)
│   │   ├── wood2.png          # Small wood (1x1)
│   │   ├── wood3.png          # Stump (1x1)
│   │   ├── Mushroom.png       # Mushroom (1x1)
│   │   └── Street lamp.png    # Street lamp (1x3)
│   └── insidetiles/          # Indoor map tiles
│       ├── 室内地板.png       # Indoor floor (1x1)
│       ├── 室内墙.png         # Wall (1x1)
│       ├── 室内床.png         # Bed (2x3)
│       ├── 室内桌子.png       # Table (2x2)
│       └── ...
├── examples/                  # Example files
│   ├── map_layout.json        # Outdoor map config example
│   ├── indoor_template.json   # Indoor map config example
│   ├── indoor_map.json        # Indoor map example
│   └── test_floor.json        # Test config
├── tools/                     # Tool scripts
│   ├── map_renderer.py        # Map renderer (core)
│   ├── tile_selector.py       # Tile selector GUI
│   ├── tile_annotator.py      # Multi-tile annotation tool
│   └── analyze_tiles.py       # Tile analysis tool
├── prompts/                   # AI prompts
│   ├── 提示词.txt             # Outdoor map generation prompt
│   └── 室内提示词.txt         # Indoor map generation prompt
├── docs/                      # Documentation
│   ├── tiles_list.txt         # Outdoor tiles list
│   ├── insidetiles_list.txt   # Indoor tiles list
│   └── tile_selector_readme.txt
├── output/                    # Output directory
│   └── output_map.png         # Rendered result
└── README_en.md              # English documentation
```

## Installation

### Dependencies

```bash
pip install Pillow
```

Pillow is the only external dependency, used for image processing.

## Usage

### 1. Map Renderer (Core Tool)

Render JSON config files to generate map images:

```bash
# Default render
python tools/map_renderer.py

# Specify config file
python tools/map_renderer.py examples/map_layout.json

# Specify tiles directory
python tools/map_renderer.py -t assets/tiles
```

Output: `output/output_map.png`

### 2. Tile Selector

A GUI tool for selecting and cropping tiles from larger images:

```bash
python tools/tile_selector.py
```

Features:
- Open image files
- Drag to select regions
- Export selected regions as individual images

### 3. Tile Annotator

Tool for annotating multi-tile object positions and sizes:

```bash
python tools/tile_annotator.py
# Requires image path, e.g.:
# python tools/tile_annotator.py "path/to/tileset.png"
```

Features:
- Display grid lines
- Select multi-tile regions
- Save annotation config

### 4. Tile Analyzer

Analyze image specifications in a tileset directory:

```bash
# Analyze indoor tiles
python tools/analyze_tiles.py assets/insidetiles

# Analyze outdoor tiles
python tools/analyze_tiles.py assets/tiles
```

## JSON Config Format

### Basic Structure

```json
{
  "mapName": "Map Name",
  "tileSize": 32,
  "width": 20,
  "height": 15,
  "defaultTile": "grass",
  "layers": [...]
}
```

### Layer Types

1. **procedural**: Procedural generation
   - `rectangle`: Rectangular area
   - `circle`: Circular area
   - `line`: Straight line

2. **grid**: Complete 2D array

3. **sparse**: Sparse array, only listing object positions

### Example

```json
{
  "layers": [
    {
      "name": "Ground Layer",
      "type": "procedural",
      "rules": [
        {"type": "rectangle", "tile": "road", "x1": 5, "y1": 4, "x2": 14, "y2": 10}
      ]
    },
    {
      "name": "Objects Layer",
      "type": "sparse",
      "data": [
        {"tile": "house", "x": 3, "y": 3},
        {"tile": "tree", "x": 2, "y": 2}
      ]
    }
  ]
}
```

## AI-Assisted Generation

Use the prompt files in `prompts/` directory with AI to generate map layout JSON:

1. Copy the prompt for AI
2. Describe the map you want
3. AI generates JSON config
4. Save as JSON file
5. Use renderer to generate map

## Asset Specifications

- Tile size: 32x32 pixels
- Supported formats: PNG, JPG, BMP
- Multi-tile objects: Automatically calculated based on image size

---

# Technical Documentation

## 1. Problem Definition: What are we solving? What's wrong with existing solutions?

### Core Problem
RPG game map creation is a time-consuming process with high technical barriers. Traditional solutions have the following issues:

**Pain points of existing solutions:**
1. **Inefficient manual layout**: Traditional map editors require placing tiles one by one, creating a 20x15 map requires manually placing 300 tiles
2. **Steep learning curve**: Professional map editors (like Tiled, RPG Maker) require learning complex interfaces and operations
3. **Difficult AI integration**: Existing tools cannot directly utilize AI to generate map layouts, requiring manual conversion
4. **Complex asset management**: Multi-tile objects (like houses, trees) require manual calculation of size and position
5. **Lack of procedural generation**: Difficult to batch generate map variants with similar styles

### Our Solution
Txt To RPG Map solves the above problems through:
- **Natural language description** → **AI generates JSON** → **Automatic map rendering**
- Simplified workflow: Reduces from hours of manual layout to minutes of AI-assisted generation
- Zero-configuration dependency: Only requires Pillow library, no database or complex environment needed
- Intelligent asset recognition: Automatically detects tile size, supports multi-tile objects

## 2. Architecture Overview: How is the system organized? Diagram + Text

### System Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                   User Input Layer                          │
├─────────────────────────────────────────────────────────────┤
│ 1. Natural Language  │ 2. JSON Config      │ 3. GUI Tools   │
│   "Forest Village"   │   map_layout.json   │   tile_selector.py │
└─────────────────────┴──────────────────────┴─────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Core Processing Layer                      │
├─────────────────────────────────────────────────────────────┤
│  map_renderer.py ──┐                                         │
│  • Config parsing  │                                         │
│  • Layer compositing├──▶ Rendering Engine                   │
│  • Collision detection│    • Procedural generation           │
│  • Multi-tile handling│      (rectangles/circles/lines)      │
│                    │    • Sparse array optimization         │
│  analyze_tiles.py ─┘    • Layer stacking algorithm          │
│  • Asset analysis  │                                         │
│  • Size detection  │                                         │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Asset Management Layer                     │
├─────────────────────────────────────────────────────────────┤
│  assets/                    │  tools/                       │
│  ├── tiles/       (outdoor)│  ├── tile_annotator.py        │
│  │   ├── grass.png         │  │   • Multi-tile annotation  │
│  │   ├── tree.png (4x5)    │  │   • Grid display           │
│  │   └── ...               │  │                           │
│  └── insidetiles/ (indoor) │  └── tile_selector.py        │
│      ├── wall.png          │      • Tile selector          │
│      ├── bed.png (2x3)     │      • Region cropping        │
│      └── ...               │                               │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Output Layer                              │
├─────────────────────────────────────────────────────────────┤
│  output/output_map.png      │  docs/                        │
│  • PNG format map           │  • tiles_list.txt            │
│  • Alpha channel support    │  • Asset documentation       │
│  • Layered rendering result │                               │
└─────────────────────────────────────────────────────────────┘
```

### Core Component Description

**1. Rendering Engine (map_renderer.py)**
- Configuration-driven: Generates maps based on JSON config files
- Layer system: Supports ground/object/decorative multi-layer stacking
- Procedural generation: Basic shapes like rectangles, circles, lines
- Collision detection: Prevents object overlap (configurable)

**2. Asset Management System**
- Automatic size detection: Calculates tile size based on image pixels
- Alias mapping: Supports English name to Chinese filename mapping
- Multi-tile support: Automatically handles large objects like 4x5 trees, 5x6 houses

**3. Auxiliary Toolset**
- Tile selector: Crops individual tiles from larger images
- Tile annotator: Annotates size and position of multi-tile objects
- Asset analyzer: Analyzes specifications of all tiles in a directory

## 3. Core Innovations: What's unique about our design? Pseudocode/Flowcharts

### Innovation 1: AI-friendly JSON Configuration Format
```json
{
  "mapName": "Forest Village",
  "tileSize": 32,
  "width": 20,
  "height": 15,
  "defaultTile": "grass",
  "layers": [
    {
      "name": "Ground Layer",
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

### Innovation 2: Intelligent Layer Composition Algorithm
```python
# Pseudocode: Core map rendering algorithm
def render_map(config, tileset):
    # 1. Create canvas
    canvas = create_canvas(config.width, config.height)
    
    # 2. Render each layer in order
    for layer in config.layers:
        if layer.type == "procedural":
            render_procedural_layer(canvas, layer, tileset)
        elif layer.type == "grid":
            render_grid_layer(canvas, layer, tileset)
        elif layer.type == "sparse":
            render_sparse_layer(canvas, layer, tileset)
    
    # 3. Apply collision detection (optional)
    if config.enable_collision:
        apply_collision_detection(canvas)
    
    return canvas

# Procedural layer rendering
def render_procedural_layer(canvas, layer, tileset):
    for rule in layer.rules:
        if rule.type == "rectangle":
            fill_rectangle(canvas, rule, tileset[rule.tile])
        elif rule.type == "circle":
            fill_circle(canvas, rule, tileset[rule.tile])
        elif rule.type == "line":
            draw_line(canvas, rule, tileset[rule.tile])
```

### Innovation 3: Automatic Multi-tile Object Processing
```
Flowchart: Multi-tile object rendering process
Start
  ↓
Read image → Calculate size (width/height/tile_size)
  ↓
Determine tile type:
  • Single tile (1x1) → Store directly
  • Multi-tile (NxM) → Record size information
  ↓
During rendering:
  if multi-tile object:
      for dy in range(object_height):
          for dx in range(object_width):
              Calculate subtile position (x+dx, y+dy)
              Render subtile
  else:
      Render single tile directly
  ↓
End
```

### Innovation 4: Zero-configuration Asset Expansion
```python
# Asset auto-discovery mechanism
def discover_assets(asset_dir):
    assets = {}
    for file in os.listdir(asset_dir):
        if is_image_file(file):
            name = remove_extension(file)
            img = load_image(file)
            size = calculate_tile_size(img)  # Auto-calculate: 32x32=1x1, 128x160=4x5
            assets[name] = {
                "image": img,
                "width": size[0],  # Tile width
                "height": size[1], # Tile height
                "is_multi": size[0] > 1 or size[1] > 1
            }
    return assets
```







