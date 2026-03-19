import json
import os
import glob
from PIL import Image
from typing import Dict, List, Tuple, Optional

TILE_SIZE = 32

ALIASES = {
    "grass": "grass",
    "tree": "tree",
    "wood": "wood",
    "house": "house",
    "road": "道路",
    "stone": "石头",
    "rock": "石头",
    "flower": "花",
    "meadow": "草地",
}

# Walls as background; not counted in global occupancy
WALL_TILES = {"室内墙"}

class MapComposer:
    def __init__(self, tileset_dir: str, tile_size: int = 32):
        self.tile_size = tile_size
        self.tileset_dir = tileset_dir
        self.single_tiles: Dict[str, Image.Image] = {}
        self.multi_tiles: Dict[str, Tuple[Tuple[int, int], Image.Image]] = {}
        self._load_tiles(tileset_dir)
    
    def _load_tiles(self, tileset_dir: str):
        if not os.path.exists(tileset_dir):
            print(f"素材目录不存在: {tileset_dir}")
            return
        
        for filename in os.listdir(tileset_dir):
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                continue
            
            filepath = os.path.join(tileset_dir, filename)
            name = os.path.splitext(filename)[0]
            
            img = Image.open(filepath).convert('RGBA')
            w, h = img.size
            
            tile_w = w // self.tile_size
            tile_h = h // self.tile_size
            
            if tile_w == 1 and tile_h == 1:
                if img.size != (self.tile_size, self.tile_size):
                    img = img.resize((self.tile_size, self.tile_size))
                self.single_tiles[name] = img
                print(f"加载单格图块: {name}")
            else:
                expected_size = (tile_w * self.tile_size, tile_h * self.tile_size)
                if img.size != expected_size:
                    img = img.resize(expected_size)
                self.multi_tiles[name] = ((tile_w, tile_h), img)
                print(f"加载多格图块: {name} ({tile_w}x{tile_h})")
    
    def compose(self, map_json: dict, output_path: str):
        width = map_json.get('width', 10)
        height = map_json.get('height', 10)
        tile_size = map_json.get('tileSize', self.tile_size)
        default_tile = map_json.get('defaultTile', 'grass')
        layers = map_json.get('layers', [])
        
        map_img = Image.new('RGBA', (width * tile_size, height * tile_size), (0, 0, 0, 0))
        
        occupied = [[False] * width for _ in range(height)]
        
        for layer in layers:
            layer_name = layer.get('name', 'unknown')
            layer_type = layer.get('type', 'grid')
            data = layer.get('data', [])
            
            print(f"处理图层: {layer_name} ({layer_type})")
            
            if layer_type == 'grid':
                layer_occupied = [[False] * width for _ in range(height)]
                self._render_grid_layer(map_img, data, width, height, tile_size, layer_occupied)
            elif layer_type == 'procedural':
                layer_occupied = [[False] * width for _ in range(height)]
                rules = layer.get('rules', [])
                grid_data = self._generate_procedural(width, height, default_tile, rules, layer_occupied)
                self._render_grid_layer(map_img, grid_data, width, height, tile_size, layer_occupied)
            elif layer_type == 'sparse':
                self._render_sparse_layer(map_img, data, tile_size, occupied, width, height)
        
        map_img.save(output_path)
        print(f"地图已保存: {output_path}")
    
    def _generate_procedural(self, width: int, height: int, default_tile: str, rules: list, occupied: list) -> List[List[str]]:
        grid = [[default_tile for _ in range(width)] for _ in range(height)]
        
        for rule in rules:
            rule_type = rule.get('type')
            
            if rule_type == 'rectangle':
                tile = rule.get('tile')
                x1 = rule.get('x1', 0)
                y1 = rule.get('y1', 0)
                x2 = rule.get('x2', width - 1)
                y2 = rule.get('y2', height - 1)
                
                is_multi = tile in self.multi_tiles
                if is_multi:
                    (mw, mh) = self.multi_tiles[tile][0]
                else:
                    mw = mh = 1
                
                for y in range(y1, y2 + 1):
                    for x in range(x1, x2 + 1):
                        if 0 <= x < width and 0 <= y < height:
                            if is_multi:
                                can_place = all(
                                    0 <= x + dx < width and 0 <= y + dy < height and not occupied[y + dy][x + dx]
                                    for dy in range(mh) for dx in range(mw)
                                )
                                if can_place:
                                    grid[y][x] = tile
                                    for dy in range(mh):
                                        for dx in range(mw):
                                            occupied[y + dy][x + dx] = True
                            else:
                                if not occupied[y][x]:
                                    grid[y][x] = tile
                                    if tile not in WALL_TILES:
                                        occupied[y][x] = True
            
            elif rule_type == 'circle':
                tile = rule.get('tile')
                cx = rule.get('centerX', 0)
                cy = rule.get('centerY', 0)
                r = rule.get('radius', 1)
                
                is_multi = tile in self.multi_tiles
                if is_multi:
                    (mw, mh) = self.multi_tiles[tile][0]
                else:
                    mw = mh = 1
                
                for y in range(max(0, cy - r), min(height, cy + r + 1)):
                    for x in range(max(0, cx - r), min(width, cx + r + 1)):
                        if (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2:
                            if is_multi:
                                can_place = all(
                                    0 <= x + dx < width and 0 <= y + dy < height and not occupied[y + dy][x + dx]
                                    for dy in range(mh) for dx in range(mw)
                                )
                                if can_place:
                                    grid[y][x] = tile
                                    for dy in range(mh):
                                        for dx in range(mw):
                                            occupied[y + dy][x + dx] = True
                            else:
                                if not occupied[y][x]:
                                    grid[y][x] = tile
                                    if tile not in WALL_TILES:
                                        occupied[y][x] = True
            
            elif rule_type == 'line':
                tile = rule.get('tile')
                x1, y1 = rule.get('x1', 0), rule.get('y1', 0)
                x2, y2 = rule.get('x2', 0), rule.get('y2', 0)
                points = self._bresenham_line(x1, y1, x2, y2)
                
                is_multi = tile in self.multi_tiles
                if is_multi:
                    (mw, mh) = self.multi_tiles[tile][0]
                else:
                    mw = mh = 1
                
                for x, y in points:
                    if 0 <= x < width and 0 <= y < height:
                        if is_multi:
                            can_place = all(
                                0 <= x + dx < width and 0 <= y + dy < height and not occupied[y + dy][x + dx]
                                for dy in range(mh) for dx in range(mw)
                            )
                            if can_place:
                                grid[y][x] = tile
                                for dy in range(mh):
                                    for dx in range(mw):
                                        occupied[y + dy][x + dx] = True
                        else:
                            if not occupied[y][x]:
                                grid[y][x] = tile
                                occupied[y][x] = True
        
        return grid
    
    def _bresenham_line(self, x1: int, y1: int, x2: int, y2: int) -> list:
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        while True:
            points.append((x, y))
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        return points
    
    def _resolve_alias(self, tile_name: Optional[str]) -> str:
        if tile_name is None:
            return ""
        
        if tile_name in self.single_tiles or tile_name in self.multi_tiles:
            return tile_name
        
        return tile_name or ""
    
    def _render_grid_layer(self, map_img: Image.Image, grid_data: List[List[str]], 
                           width: int, height: int, tile_size: int, occupied: List[List[bool]] = None):
        if occupied is None:
            occupied = [[False] * width for _ in range(height)]
        
        for y in range(min(height, len(grid_data))):
            row = grid_data[y]
            for x in range(min(width, len(row))):
                tile_name = self._resolve_alias(row[x])
                if tile_name in WALL_TILES:
                    if tile_name in self.multi_tiles:
                        (mw, mh), tile_img = self.multi_tiles[tile_name]
                        map_img.paste(tile_img, (x * tile_size, y * tile_size), tile_img)
                    elif tile_name in self.single_tiles:
                        tile_img = self.single_tiles[tile_name]
                        map_img.paste(tile_img, (x * tile_size, y * tile_size), tile_img)
                    continue
                
                if tile_name in self.multi_tiles:
                    (mw, mh), tile_img = self.multi_tiles[tile_name]
                    can_place = all(
                        0 <= x + dx < width and 0 <= y + dy < height and not occupied[y + dy][x + dx]
                        for dy in range(mh) for dx in range(mw)
                    )
                    if can_place:
                        map_img.paste(tile_img, (x * tile_size, y * tile_size), tile_img)
                        for dy in range(mh):
                            for dx in range(mw):
                                occupied[y + dy][x + dx] = True
                elif tile_name in self.single_tiles:
                    tile_img = self.single_tiles[tile_name]
                    map_img.paste(tile_img, (x * tile_size, y * tile_size), tile_img)
                    occupied[y][x] = True
    
    def _render_sparse_layer(self, map_img: Image.Image, objects: List[dict], 
                              tile_size: int, occupied: List[List[bool]], 
                              map_width: int, map_height: int):
        for obj in objects:
            tile_name = self._resolve_alias(obj.get('tile'))
            x = obj.get('x', 0)
            y = obj.get('y', 0)
            w = obj.get('width', 1)
            h = obj.get('height', 1)
            
            if tile_name in self.multi_tiles:
                (mw, mh), img = self.multi_tiles[tile_name]
                w, h = mw, mh
            elif tile_name in self.single_tiles:
                img = self.single_tiles[tile_name]
                w = h = 1
            else:
                print(f"警告: 未知图块 '{tile_name}'")
                continue
            
            if x + w > map_width or y + h > map_height:
                print(f"警告: 物体 {tile_name} 超出边界")
                continue
            
            overlap = any(occupied[y + dy][x + dx] for dy in range(h) for dx in range(w))
            if overlap:
                print(f"警告: 物体 {tile_name} 与其他物体重叠，跳过")
                continue
            
            map_img.paste(img, (x * tile_size, y * tile_size), img)
            
            for dy in range(h):
                for dx in range(w):
                    occupied[y + dy][x + dx] = True


def find_tileset_dir():
    for name in ['tiles', 'tileset', '素材', 'assets']:
        if os.path.exists(name):
            return name
    for subdir in ['地图素材包/Autotiles', '地图素材包/地图']:
        if os.path.exists(subdir):
            return subdir
    if os.path.exists('009-CastleTown01复刻'):
        return '009-CastleTown01复刻'
    return 'tiles'


json_layout = """
{
  "mapName": "森林营地",
  "tileSize": 32,
  "width": 20,
  "height": 15,
  "defaultTile": "grass",
  "layers": [
    {
      "name": "地面层",
      "type": "grid",
      "data": [
        ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
        ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
        ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
        ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
        ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
        ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
        ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
        ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
        ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
        ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
        ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
        ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
        ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
        ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
        ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"]
      ]
    },
    {
      "name": "道路层",
      "type": "sparse",
      "data": [
        {"tile": "road", "x": 2, "y": 5},
        {"tile": "road", "x": 3, "y": 5},
        {"tile": "road", "x": 4, "y": 5},
        {"tile": "road", "x": 5, "y": 5},
        {"tile": "road", "x": 6, "y": 5},
        {"tile": "road", "x": 7, "y": 5},
        {"tile": "road", "x": 8, "y": 5},
        {"tile": "road", "x": 9, "y": 5},
        {"tile": "road", "x": 10, "y": 5},
        {"tile": "road", "x": 11, "y": 5},
        {"tile": "road", "x": 12, "y": 5},
        {"tile": "road", "x": 13, "y": 5},
        {"tile": "road", "x": 14, "y": 5},
        {"tile": "road", "x": 15, "y": 5},
        {"tile": "road", "x": 16, "y": 5},
        {"tile": "road", "x": 17, "y": 5},
        {"tile": "road", "x": 17, "y": 4},
        {"tile": "road", "x": 17, "y": 3},
        {"tile": "road", "x": 16, "y": 3},
        {"tile": "road", "x": 15, "y": 3},
        {"tile": "road", "x": 14, "y": 3},
        {"tile": "road", "x": 13, "y": 3},
        {"tile": "road", "x": 12, "y": 3},
        {"tile": "road", "x": 11, "y": 3},
        {"tile": "road", "x": 10, "y": 3},
        {"tile": "road", "x": 9, "y": 3},
        {"tile": "road", "x": 8, "y": 3}
      ]
    },
    {
      "name": "主要物体层",
      "type": "sparse",
      "data": [
        {"tile": "house", "x": 7, "y": 6},
        {"tile": "tree", "x": 2, "y": 2},
        {"tile": "tree", "x": 15, "y": 10},
        {"tile": "tree", "x": 4, "y": 12},
        {"tile": "tree", "x": 12, "y": 1},
        {"tile": "tree", "x": 17, "y": 7},
        {"tile": "wood", "x": 9, "y": 1},
        {"tile": "wood", "x": 1, "y": 9},
        {"tile": "wood", "x": 5, "y": 8},
        {"tile": "Street lamp", "x": 18, "y": 2}
      ]
    },
    {
      "name": "装饰层",
      "type": "sparse",
      "data": [
        {"tile": "flower", "x": 3, "y": 3},
        {"tile": "flower", "x": 14, "y": 4},
        {"tile": "flower", "x": 6, "y": 13},
        {"tile": "flower", "x": 19, "y": 11},
        {"tile": "Mushroom", "x": 2, "y": 7},
        {"tile": "Mushroom", "x": 11, "y": 12},
        {"tile": "Mushroom", "x": 8, "y": 10},
        {"tile": "wood2", "x": 13, "y": 8},
        {"tile": "wood2", "x": 16, "y": 13},
        {"tile": "wood3", "x": 0, "y": 12},
        {"tile": "wood3", "x": 10, "y": 7},
        {"tile": "flower", "x": 18, "y": 9}
      ]
    }
  ]
}
"""

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('json_file', nargs='?', default='map_layout.json')
    parser.add_argument('-t', '--tiles', default='tiles', help='素材目录 (默认: tiles)')
    args = parser.parse_args()
    
    tileset_dir = args.tiles
    if not os.path.exists(tileset_dir):
        print(f"素材目录不存在: {tileset_dir}")
        sys.exit(1)
    
    print(f"素材目录: {tileset_dir}")
    
    composer = MapComposer(tileset_dir)
    print(f"可用单格图块: {list(composer.single_tiles.keys())}")
    print(f"可用多格图块: {list(composer.multi_tiles.keys())}")
    
    json_file = args.json_file
    
    if not os.path.exists(json_file):
        print(f"JSON文件不存在: {json_file}")
        print("用法: python map_renderer.py [json文件]")
        sys.exit(1)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        map_data = json.load(f)
    
    composer.compose(map_data, "output_map.png")
