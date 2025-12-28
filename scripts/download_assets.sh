#!/bin/bash
# Download free 3D assets for Text-to-3D World Builder
# Sources: quaternius.com, kaylousberg, pmnd.rs, etc.

set -e

ASSETS_DIR="/home/byunghyun/workspace/github/text_to_3d_world_builder/client/public/assets/models"

echo "=== Downloading 3D Assets ==="

# Function to download with retry
download() {
    local url=$1
    local output=$2
    echo "Downloading: $output"
    curl -L -f -o "$output" "$url" 2>/dev/null || echo "  Failed: $url"
}

# ============================================================
# FURNITURE
# ============================================================
echo ""
echo "=== Furniture ==="
cd "$ASSETS_DIR/furniture"

# From market.pmnd.rs / drei examples
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/armchair/model.gltf" "armchair.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/sofa/model.gltf" "sofa.gltf"

# From quaternius (low poly packs) - direct GitHub raw
QUATERNIUS_BASE="https://raw.githubusercontent.com/quaternius/lowpoly-furniture/main"

# Alternative: vazxmithril's models (commonly used in R3F)
VAZXMITHRIL="https://vazxmithril.nyc3.cdn.digitaloceanspaces.com/hdri"

# Try some known working URLs
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/low-poly-table/model.gltf" "table.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/couch/model.gltf" "couch.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/office-chair/model.gltf" "office_chair.gltf"

# ============================================================
# LIGHTING
# ============================================================
echo ""
echo "=== Lighting ==="
cd "$ASSETS_DIR/lighting"

download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/floor-lamp/model.gltf" "floor_lamp.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/desk-lamp/model.gltf" "desk_lamp.gltf"

# ============================================================
# DECOR
# ============================================================
echo ""
echo "=== Decor ==="
cd "$ASSETS_DIR/decor"

download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/plant/model.gltf" "plant.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/potted-plant/model.gltf" "potted_plant.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/picture-frame/model.gltf" "picture_frame.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/vase/model.gltf" "vase.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/clock/model.gltf" "clock.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/books/model.gltf" "books.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/rug/model.gltf" "rug.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/curtains/model.gltf" "curtains.gltf"

# ============================================================
# OFFICE
# ============================================================
echo ""
echo "=== Office ==="
cd "$ASSETS_DIR/office"

download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/desk/model.gltf" "desk.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/computer/model.gltf" "computer.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/monitor/model.gltf" "monitor.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/keyboard/model.gltf" "keyboard.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/bookshelf/model.gltf" "bookshelf.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/filing-cabinet/model.gltf" "filing_cabinet.gltf"

# ============================================================
# KITCHEN
# ============================================================
echo ""
echo "=== Kitchen ==="
cd "$ASSETS_DIR/kitchen"

download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/refrigerator/model.gltf" "refrigerator.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/microwave/model.gltf" "microwave.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/kitchen-cabinet/model.gltf" "cabinet.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/stove/model.gltf" "stove.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/sink/model.gltf" "sink.gltf"

# ============================================================
# BATHROOM
# ============================================================
echo ""
echo "=== Bathroom ==="
cd "$ASSETS_DIR/bathroom"

download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/toilet/model.gltf" "toilet.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/bathtub/model.gltf" "bathtub.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/bathroom-sink/model.gltf" "sink.gltf"
download "https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/mirror/model.gltf" "mirror.gltf"

echo ""
echo "=== Download Complete ==="
echo "Checking results..."
find "$ASSETS_DIR" -name "*.gltf" -o -name "*.glb" | wc -l
echo " files downloaded"
