import os
from PIL import Image
from collections import defaultdict

def analyze_tileset(tileset_dir: str):
    if not os.path.exists(tileset_dir):
        print(f"目录不存在: {tileset_dir}")
        return

    single_tiles = {}
    multi_tiles = {}

    for filename in os.listdir(tileset_dir):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            continue

        filepath = os.path.join(tileset_dir, filename)
        name = os.path.splitext(filename)[0]

        try:
            img = Image.open(filepath)
            w, h = img.size
            tile_w = w // 32
            tile_h = h // 32

            if tile_w == 1 and tile_h == 1:
                single_tiles[name] = (w, h)
            else:
                multi_tiles[name] = (w, h, tile_w, tile_h)
        except Exception as e:
            print(f"读取失败 {filename}: {e}")

    print(f"\n=== {tileset_dir} 素材分析 ===")
    print(f"\n单格图块 (1x1): {len(single_tiles)}")
    for name in sorted(single_tiles.keys()):
        print(f"  - {name}")

    print(f"\n多格图块: {len(multi_tiles)}")
    for name in sorted(multi_tiles.keys()):
        w, h, tw, th = multi_tiles[name]
        print(f"  - {name} ({w}x{h}) -> {tw}x{th}")

    print(f"\n=== JSON模板 ===")
    print("\n可用单格:")
    for name in sorted(single_tiles.keys()):
        print(f"  - {name}")

    print("\n可用多格:")
    for name in sorted(multi_tiles.keys()):
        w, h, tw, th = multi_tiles[name]
        print(f"  - {name} ({tw}x{th})")

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="分析素材库图片大小")
    parser.add_argument('dir', nargs='?', default='insidetiles', help='素材目录')
    args = parser.parse_args()

    analyze_tileset(args.dir)
