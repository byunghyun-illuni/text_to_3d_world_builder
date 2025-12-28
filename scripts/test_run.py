import os
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

from PIL import Image
import torch

# Local model paths from ModelScope
DINOV3_LOCAL_PATH = "/home/byunghyun/.cache/modelscope/facebook/dinov3-vitl16-pretrain-lvd1689m"
RMBG_LOCAL_PATH = "/home/byunghyun/.cache/modelscope/briaai/RMBG-2.0"

# Monkey-patch DinoV3 to use local model
from trellis2.modules import image_feature_extractor
OriginalDinoV3FeatureExtractor = image_feature_extractor.DinoV3FeatureExtractor

class PatchedDinoV3FeatureExtractor(OriginalDinoV3FeatureExtractor):
    def __init__(self, model_name: str, image_size=512):
        if "dinov3-vitl16" in model_name:
            model_name = DINOV3_LOCAL_PATH
            print(f"Using local DINOv3 model from: {model_name}")
        super().__init__(model_name, image_size)

image_feature_extractor.DinoV3FeatureExtractor = PatchedDinoV3FeatureExtractor

# Monkey-patch BiRefNet to use local model
from trellis2.pipelines import rembg as rembg_module
OriginalBiRefNet = rembg_module.BiRefNet

class PatchedBiRefNet(OriginalBiRefNet):
    def __init__(self, model_name: str):
        if "RMBG-2.0" in model_name:
            model_name = RMBG_LOCAL_PATH
            print(f"Using local RMBG-2.0 model from: {model_name}")
        super().__init__(model_name)

rembg_module.BiRefNet = PatchedBiRefNet

from trellis2.pipelines import Trellis2ImageTo3DPipeline
import o_voxel

print("Loading pipeline... (첫 실행 시 모델 다운로드)")
pipeline = Trellis2ImageTo3DPipeline.from_pretrained("microsoft/TRELLIS.2-4B")
pipeline.cuda()

print("Loading image...")
image = Image.open("assets/example_image/T.png")
print(f"Image size: {image.size}")

print("Generating 3D mesh... (RTX 3090에서 약 10-30초 소요)")
mesh = pipeline.run(image)[0]

print(f"Mesh vertices: {mesh.vertices.shape}")
print(f"Mesh faces: {mesh.faces.shape}")

# Simplify for export
mesh.simplify(1000000)

# Export to GLB
print("Exporting to GLB...")
glb = o_voxel.postprocess.to_glb(
    vertices=mesh.vertices,
    faces=mesh.faces,
    attr_volume=mesh.attrs,
    coords=mesh.coords,
    attr_layout=mesh.layout,
    voxel_size=mesh.voxel_size,
    aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
    decimation_target=100000,
    texture_size=2048,
    remesh=True,
)
glb.export("test_output.glb", extension_webp=True)

print("✅ Success! Output saved to test_output.glb")
print(f"GPU Memory used: {torch.cuda.max_memory_allocated() / 1024**3:.2f} GB")
