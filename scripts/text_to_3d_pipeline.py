"""
Text → Image → 3D Pipeline
텍스트 설명을 받아 이미지를 생성하고, 3D 모델로 변환하는 파이프라인

사용법:
    python text_to_3d_pipeline.py "A cute cartoon robot toy"
    python text_to_3d_pipeline.py --prompt "A medieval sword" --output sword.glb
"""

import os
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import argparse
import io
from PIL import Image
import torch
from typing import Optional
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

# Gemini API 키 (환경변수 또는 직접 설정)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 로컬 모델 경로 (ModelScope에서 다운로드된 경로)
DINOV3_LOCAL_PATH = "/home/byunghyun/.cache/modelscope/facebook/dinov3-vitl16-pretrain-lvd1689m"
RMBG_LOCAL_PATH = "/home/byunghyun/.cache/modelscope/briaai/RMBG-2.0"

# 3D 생성에 최적화된 프롬프트 템플릿
PROMPT_TEMPLATE_3D = """Generate an image of: {description}

Style requirements:
- 3D rendered style, high quality
- Single object, centered in frame
- Pure white or transparent background
- Studio lighting with soft shadows
- Front view or 3/4 view angle
- Full object visible, not cropped
- Clean isolated object for 3D conversion"""


# ============================================================================
# Text-to-Image Module (Gemini/Imagen)
# ============================================================================

class TextToImageGenerator:
    """Gemini/Imagen API를 사용한 텍스트-이미지 생성기"""

    def __init__(self, api_key: str):
        from google import genai
        from google.genai import types
        self.genai = genai
        self.types = types
        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt: str, output_path: str = "generated_image.png") -> Optional[Image.Image]:
        """
        텍스트 프롬프트로 이미지를 생성합니다.

        Args:
            prompt: 생성할 이미지에 대한 설명
            output_path: 저장할 파일 경로

        Returns:
            생성된 PIL Image 객체, 실패 시 None
        """
        # 3D 변환에 최적화된 프롬프트 생성
        full_prompt = PROMPT_TEMPLATE_3D.format(description=prompt)

        # 여러 모델 순차 시도
        models = [
            ("gemini-2.0-flash-exp-image-generation", self._generate_gemini),
            ("gemini-2.5-flash-image", self._generate_gemini),
            ("imagen-4.0-generate-001", self._generate_imagen),
        ]

        for model_name, generator_fn in models:
            print(f"Trying {model_name}...")
            try:
                image = generator_fn(model_name, full_prompt)
                if image:
                    image.save(output_path)
                    print(f"Image saved to: {output_path}")
                    return image
            except Exception as e:
                print(f"{model_name} failed: {e}")
                continue

        return None

    def _generate_gemini(self, model: str, prompt: str) -> Optional[Image.Image]:
        """Gemini 모델로 이미지 생성"""
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=self.types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            )
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_data = part.inline_data.data
                return Image.open(io.BytesIO(image_data))

        return None

    def _generate_imagen(self, model: str, prompt: str) -> Optional[Image.Image]:
        """Imagen 모델로 이미지 생성"""
        response = self.client.models.generate_images(
            model=model,
            prompt=prompt,
            config=self.types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",
            )
        )

        if response.generated_images:
            image_bytes = response.generated_images[0].image.image_bytes
            return Image.open(io.BytesIO(image_bytes))

        return None


# ============================================================================
# Image-to-3D Module (TRELLIS.2)
# ============================================================================

class ImageTo3DGenerator:
    """TRELLIS.2를 사용한 이미지-3D 생성기"""

    def __init__(self):
        self.pipeline = None
        self._patch_models()

    def _patch_models(self):
        """로컬 모델 경로를 사용하도록 패치"""
        # DinoV3 패치
        from trellis2.modules import image_feature_extractor
        OriginalDinoV3 = image_feature_extractor.DinoV3FeatureExtractor

        class PatchedDinoV3(OriginalDinoV3):
            def __init__(self, model_name: str, image_size=512):
                if "dinov3-vitl16" in model_name:
                    model_name = DINOV3_LOCAL_PATH
                super().__init__(model_name, image_size)

        image_feature_extractor.DinoV3FeatureExtractor = PatchedDinoV3

        # BiRefNet 패치
        from trellis2.pipelines import rembg as rembg_module
        OriginalBiRefNet = rembg_module.BiRefNet

        class PatchedBiRefNet(OriginalBiRefNet):
            def __init__(self, model_name: str):
                if "RMBG-2.0" in model_name:
                    model_name = RMBG_LOCAL_PATH
                super().__init__(model_name)

        rembg_module.BiRefNet = PatchedBiRefNet

    def load_pipeline(self):
        """TRELLIS.2 파이프라인 로드"""
        if self.pipeline is None:
            print("Loading TRELLIS.2 pipeline...")
            from trellis2.pipelines import Trellis2ImageTo3DPipeline
            self.pipeline = Trellis2ImageTo3DPipeline.from_pretrained("microsoft/TRELLIS.2-4B")
            self.pipeline.cuda()
            print("Pipeline loaded successfully")

    def generate(
        self,
        image: Image.Image,
        output_path: str = "output.glb",
        decimation_target: int = 100000,
        texture_size: int = 2048,
    ) -> str:
        """
        이미지를 3D 모델로 변환합니다.

        Args:
            image: 입력 PIL Image
            output_path: 출력 GLB 파일 경로
            decimation_target: 메시 단순화 목표 면 수
            texture_size: 텍스처 해상도

        Returns:
            출력 파일 경로
        """
        import o_voxel

        self.load_pipeline()

        print(f"Generating 3D mesh from image ({image.size})...")
        mesh = self.pipeline.run(image)[0]

        print(f"Mesh generated: {mesh.vertices.shape[0]} vertices, {mesh.faces.shape[0]} faces")

        # 메시 단순화
        mesh.simplify(1000000)

        # GLB 내보내기
        print("Exporting to GLB...")
        glb = o_voxel.postprocess.to_glb(
            vertices=mesh.vertices,
            faces=mesh.faces,
            attr_volume=mesh.attrs,
            coords=mesh.coords,
            attr_layout=mesh.layout,
            voxel_size=mesh.voxel_size,
            aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
            decimation_target=decimation_target,
            texture_size=texture_size,
            remesh=True,
        )
        glb.export(output_path, extension_webp=True)

        print(f"3D model saved to: {output_path}")
        print(f"GPU Memory used: {torch.cuda.max_memory_allocated() / 1024**3:.2f} GB")

        return output_path


# ============================================================================
# Full Pipeline
# ============================================================================

class TextTo3DPipeline:
    """Text → Image → 3D 전체 파이프라인"""

    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.text_to_image = TextToImageGenerator(api_key)
        self.image_to_3d = ImageTo3DGenerator()

    def generate(
        self,
        text_prompt: str,
        output_path: str = "output.glb",
        keep_image: bool = True,
    ) -> dict:
        """
        텍스트 설명을 받아 3D 모델을 생성합니다.

        Args:
            text_prompt: 생성할 3D 모델에 대한 텍스트 설명
            output_path: 출력 GLB 파일 경로
            keep_image: 중간 이미지 파일 보존 여부

        Returns:
            결과 정보 딕셔너리
        """
        result = {
            "success": False,
            "prompt": text_prompt,
            "image_path": None,
            "model_path": None,
            "error": None,
        }

        # 이미지 경로 설정
        output_stem = Path(output_path).stem
        image_path = f"{output_stem}_image.png"

        # Step 1: Text → Image
        print("\n" + "=" * 60)
        print("Step 1: Text → Image (Gemini/Imagen)")
        print("=" * 60)
        print(f"Prompt: {text_prompt}")

        image = self.text_to_image.generate(text_prompt, image_path)

        if image is None:
            result["error"] = "Image generation failed"
            print(f"\n❌ {result['error']}")
            return result

        result["image_path"] = image_path
        print(f"✅ Image generated: {image_path}")

        # Step 2: Image → 3D
        print("\n" + "=" * 60)
        print("Step 2: Image → 3D (TRELLIS.2)")
        print("=" * 60)

        try:
            model_path = self.image_to_3d.generate(image, output_path)
            result["model_path"] = model_path
            result["success"] = True
            print(f"✅ 3D model generated: {model_path}")
        except Exception as e:
            result["error"] = f"3D generation failed: {e}"
            print(f"\n❌ {result['error']}")
            return result

        # 중간 이미지 삭제 (옵션)
        if not keep_image and result["image_path"]:
            os.remove(result["image_path"])
            result["image_path"] = None

        print("\n" + "=" * 60)
        print("✅ Pipeline completed successfully!")
        print("=" * 60)

        return result

    def generate_from_image(
        self,
        image_path: str,
        output_path: str = "output.glb",
    ) -> dict:
        """
        기존 이미지에서 3D 모델을 생성합니다.

        Args:
            image_path: 입력 이미지 경로
            output_path: 출력 GLB 파일 경로

        Returns:
            결과 정보 딕셔너리
        """
        result = {
            "success": False,
            "image_path": image_path,
            "model_path": None,
            "error": None,
        }

        print("\n" + "=" * 60)
        print("Image → 3D (TRELLIS.2)")
        print("=" * 60)

        try:
            image = Image.open(image_path)
            print(f"Input image: {image_path} ({image.size})")

            model_path = self.image_to_3d.generate(image, output_path)
            result["model_path"] = model_path
            result["success"] = True
            print(f"✅ 3D model generated: {model_path}")
        except Exception as e:
            result["error"] = f"3D generation failed: {e}"
            print(f"\n❌ {result['error']}")

        return result


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Text → Image → 3D Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 텍스트에서 3D 모델 생성
  python text_to_3d_pipeline.py "A cute cartoon robot"

  # 특정 출력 파일명 지정
  python text_to_3d_pipeline.py --prompt "A medieval sword" --output sword.glb

  # 기존 이미지에서 3D 모델 생성
  python text_to_3d_pipeline.py --image input.png --output model.glb
        """
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="생성할 3D 모델에 대한 텍스트 설명"
    )
    parser.add_argument(
        "--prompt", "-p",
        dest="prompt_arg",
        help="생성할 3D 모델에 대한 텍스트 설명 (대안)"
    )
    parser.add_argument(
        "--image", "-i",
        help="입력 이미지 경로 (이미지에서 3D 생성 시)"
    )
    parser.add_argument(
        "--output", "-o",
        default="output.glb",
        help="출력 GLB 파일 경로 (기본: output.glb)"
    )
    parser.add_argument(
        "--api-key",
        default=GEMINI_API_KEY,
        help="Gemini API 키"
    )
    parser.add_argument(
        "--keep-image",
        action="store_true",
        help="중간 생성 이미지 보존"
    )

    args = parser.parse_args()

    # 프롬프트 결정
    prompt = args.prompt or args.prompt_arg

    # 파이프라인 초기화
    pipeline = TextTo3DPipeline(api_key=args.api_key)

    if args.image:
        # 이미지에서 3D 생성
        result = pipeline.generate_from_image(args.image, args.output)
    elif prompt:
        # 텍스트에서 3D 생성
        result = pipeline.generate(prompt, args.output, args.keep_image)
    else:
        parser.print_help()
        return

    # 결과 출력
    if result["success"]:
        print(f"\n🎉 Success! Output: {result['model_path']}")
    else:
        print(f"\n💥 Failed: {result['error']}")
        exit(1)


if __name__ == "__main__":
    main()
