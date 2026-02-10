"""
Generate test images for Preview-PC Simulator
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def create_normal_images():
    """Create normal product images"""
    output_dir = Path("test/images/normal")
    output_dir.mkdir(parents=True, exist_ok=True)

    for i in range(6):
        img = Image.new('RGB', (800, 600), color=(50, 50, 50))
        draw = ImageDraw.Draw(img)

        # Draw border
        draw.rectangle([10, 10, 790, 590], outline=(100, 150, 200), width=5)

        # Draw text
        text = f"Product Image {i + 1}"
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (800 - text_width) // 2
        y = (600 - text_height) // 2
        draw.text((x, y), text, fill=(200, 200, 200), font=font)

        img.save(output_dir / f"product_{i + 1}.png")
        print(f"Created: {output_dir / f'product_{i + 1}.png'}")


def create_wait_image():
    """Create wait image"""
    output_dir = Path("test/images")
    output_dir.mkdir(parents=True, exist_ok=True)

    img = Image.new('RGB', (800, 600), color=(40, 40, 40))
    draw = ImageDraw.Draw(img)

    # Draw border
    draw.rectangle([10, 10, 790, 590], outline=(80, 80, 80), width=5)

    # Draw text
    text = "Wait for capture"
    try:
        font = ImageFont.truetype("arial.ttf", 50)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (800 - text_width) // 2
    y = (600 - text_height) // 2
    draw.text((x, y), text, fill=(150, 150, 150), font=font)

    img.save(output_dir / "wait.png")
    print(f"Created: {output_dir / 'wait.png'}")


def create_timeout_images():
    """Create timeout images"""
    output_dir = Path("test/images/timeout")
    output_dir.mkdir(parents=True, exist_ok=True)

    messages = [
        "Image took too long-Timeout",
        "Slow connection - Retrying...-Timeout",
        "Camera timeout - Please wait-Timeout",
        "Image loading timeout-Timeout",
        "Sensor timeout-Check conn-Timeout"
    ]

    # colors = [
    #     (60, 40, 40),
    #     (40, 60, 40),
    #     (40, 40, 60),
    #     (60, 60, 40),
    #     (60, 40, 60)
    # ]

    colors = [
        (40, 40, 40),
        (40, 40, 40),
        (40, 40, 40),
        (40, 40, 40),
        (40, 40, 40)
    ]

    for i, (msg, color) in enumerate(zip(messages, colors)):
        img = Image.new('RGB', (800, 600), color=color)
        draw = ImageDraw.Draw(img)

        # Draw border (red for timeout)
        draw.rectangle([10, 10, 790, 590], outline=(200, 50, 50), width=5)

        # Draw text
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), msg, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (800 - text_width) // 2
        y = (600 - text_height) // 2
        draw.text((x, y), msg, fill=(200, 200, 200), font=font)

        img.save(output_dir / f"timeout_{i + 1}.png")
        print(f"Created: {output_dir / f'timeout_{i + 1}.png'}")


if __name__ == "__main__":
    # create_normal_images()
    # create_wait_image()
    create_timeout_images()
    print("\nAll test images created successfully!")
