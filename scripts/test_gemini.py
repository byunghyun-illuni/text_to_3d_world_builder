"""
Gemini Text-to-Image Test
나노바나나 (Gemini 이미지 생성) API 테스트
"""
from google import genai
from google.genai import types
from PIL import Image
import io

# API 키 설정
API_KEY = "AIzaSyDkWekd121LK4QNQwlGiYDqe0Z5QGdanIw"

# 클라이언트 초기화
client = genai.Client(api_key=API_KEY)


def generate_image_gemini25(prompt: str, output_path: str = "generated_image.png") -> Image.Image:
    """
    Gemini 2.5 Flash Image를 사용하여 이미지를 생성합니다.
    """
    print(f"Generating image with Gemini 2.5 Flash Image...")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            )
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_data = part.inline_data.data
                image = Image.open(io.BytesIO(image_data))
                image.save(output_path)
                print(f"Image saved to: {output_path}")
                print(f"Image size: {image.size}")
                return image
            elif part.text:
                print(f"Text response: {part.text[:100]}")

    except Exception as e:
        print(f"Gemini 2.5 Flash Image error: {e}")

    return None


def generate_image_imagen4(prompt: str, output_path: str = "generated_image.png") -> Image.Image:
    """
    Imagen 4.0을 사용하여 이미지를 생성합니다.
    """
    print(f"Generating image with Imagen 4.0...")

    try:
        response = client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",
            )
        )

        if response.generated_images:
            image_bytes = response.generated_images[0].image.image_bytes
            image = Image.open(io.BytesIO(image_bytes))
            image.save(output_path)
            print(f"Image saved to: {output_path}")
            print(f"Image size: {image.size}")
            return image

    except Exception as e:
        print(f"Imagen 4.0 error: {e}")

    return None


def generate_image_gemini20(prompt: str, output_path: str = "generated_image.png") -> Image.Image:
    """
    Gemini 2.0 Flash (non-exp)를 사용하여 이미지를 생성합니다.
    """
    print(f"Generating image with Gemini 2.0 Flash...")

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            )
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_data = part.inline_data.data
                image = Image.open(io.BytesIO(image_data))
                image.save(output_path)
                print(f"Image saved to: {output_path}")
                print(f"Image size: {image.size}")
                return image

    except Exception as e:
        print(f"Gemini 2.0 Flash error: {e}")

    return None


if __name__ == "__main__":
    # 3D 변환에 적합한 이미지 생성 테스트
    prompt = """A cute cartoon robot toy, 3D rendered style,
centered in frame, pure white background,
studio lighting, high quality render,
front view, full body visible, isolated object"""

    print("=" * 50)
    print("Testing Gemini/Imagen Text-to-Image")
    print("=" * 50)

    # 1. Gemini 2.0 Flash 시도
    image = generate_image_gemini20(prompt, "generated_robot.png")

    # 2. 실패하면 Gemini 2.5 Flash Image 시도
    if not image:
        print("\nTrying Gemini 2.5 Flash Image...")
        image = generate_image_gemini25(prompt, "generated_robot.png")

    # 3. 실패하면 Imagen 4.0 시도
    if not image:
        print("\nTrying Imagen 4.0...")
        image = generate_image_imagen4(prompt, "generated_robot.png")

    if image:
        print("\n" + "=" * 50)
        print("✅ Image generation successful!")
        print(f"Image mode: {image.mode}")
        print(f"Image size: {image.size}")
        print("=" * 50)
    else:
        print("\n❌ All image generation methods failed")
        print("API quota may be exhausted. Try again later.")
