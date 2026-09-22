# To run this script, you need to install the Pillow library:
# pip install Pillow

import os
import argparse
from PIL import Image, ImageDraw, ImageFont

def get_text_watermark_position(image_size, text_size, position="bottom-right", padding=20):
    """
    Calculates the (x, y) coordinates for the text watermark based on position.
    """
    img_width, img_height = image_size
    text_width, text_height = text_size

    if position == "top-left":
        x = padding
        y = padding
    elif position == "top-right":
        x = img_width - text_width - padding
        y = padding
    elif position == "bottom-left":
        x = padding
        y = img_height - text_height - padding
    elif position == "center":
        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2
    else: # Default to "bottom-right"
        x = img_width - text_width - padding
        y = img_height - text_height - padding
    return x, y

def add_text_watermark(input_image_path, output_image_path, watermark_text,
                       font_path="arial.ttf", font_size=40, text_color=(0, 0, 0, 128),
                       position="bottom-right", padding=20):
    """
    Adds a text watermark to an image.

    Args:
        input_image_path (str): Path to the input image.
        output_image_path (str): Path to save the watermarked image.
        watermark_text (str): The text string to use as a watermark.
        font_path (str): Path to the TrueType font file (e.g., "arial.ttf").
                         Uses a default system font if not found.
        font_size (int): Size of the watermark text.
        text_color (tuple): RGBA tuple for text color (e.g., (0, 0, 0, 128) for semi-transparent black).
        position (str): Placement of the watermark ("top-left", "top-right",
                        "bottom-left", "bottom-right", "center").
        padding (int): Padding from the image edges.
    """
    try:
        # Open the input image
        original_img = Image.open(input_image_path).convert("RGBA")
    except FileNotFoundError:
        print(f"Error: Input image not found at '{input_image_path}'")
        return
    except Exception as e:
        print(f"Error opening image '{input_image_path}': {e}")
        return

    # Create a transparent layer for the watermark
    watermark_layer = Image.new("RGBA", original_img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark_layer)

    # Load font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Warning: Font '{font_path}' not found. Using default Pillow font.")
        font = ImageFont.load_default()
        # Fallback for font size if default font doesn't handle size parameter
        # (load_default doesn't take size, so we might need to adjust text_size calc)
        # For simplicity, we'll proceed assuming default font is fine or users provide path.
        # A more robust solution might render text to temporary image to get size.
        # For now, we'll calculate size based on a simpler method.

    # Get text bounding box to calculate its size.
    # textbbox requires a dummy (0,0) position to get size without actual drawing
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate text position
    x, y = get_text_watermark_position(original_img.size, (text_width, text_height), position, padding)

    # Draw the watermark text on the transparent layer
    draw.text((x, y), watermark_text, font=font, fill=text_color)

    # Combine the original image with the watermark layer
    # Image.alpha_composite combines two RGBA images based on their alpha channels
    watermarked_img = Image.alpha_composite(original_img, watermark_layer)

    # Save the output image
    try:
        # Convert to RGB before saving as JPEG to avoid issues with alpha channel
        if output_image_path.lower().endswith(('.jpg', '.jpeg')):
            watermarked_img = watermarked_img.convert("RGB")
        watermarked_img.save(output_image_path)
        print(f"Text watermark added successfully. Saved to: {output_image_path}")
    except Exception as e:
        print(f"Error saving image to '{output_image_path}': {e}")

def apply_image_opacity(image, opacity):
    """
    Applies a uniform opacity to an RGBA image.
    Opacity should be a float between 0.0 (fully transparent) and 1.0 (fully opaque).
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    alpha = image.split()[3]  # Get the alpha channel
    # Scale the alpha values by the desired opacity
    # p * opacity means 0-255 scaled by opacity (e.g., 255 * 0.5 = 127)
    alpha = alpha.point(lambda p: int(p * opacity))
    image.putalpha(alpha)
    return image

def get_image_watermark_position(base_image_size, watermark_size, position="bottom-right", padding=20):
    """
    Calculates the (x, y) coordinates for the image watermark based on position.
    """
    base_width, base_height = base_image_size
    watermark_width, watermark_height = watermark_size

    if position == "top-left":
        x = padding
        y = padding
    elif position == "top-right":
        x = base_width - watermark_width - padding
        y = padding
    elif position == "bottom-left":
        x = padding
        y = base_height - watermark_height - padding
    elif position == "center":
        x = (base_width - watermark_width) // 2
        y = (base_height - watermark_height) // 2
    else: # Default to "bottom-right"
        x = base_width - watermark_width - padding
        y = base_height - watermark_height - padding
    return x, y

def add_image_watermark(input_image_path, output_image_path, watermark_image_path,
                        position="bottom-right", scale_factor=0.2, opacity=0.5, padding=20):
    """
    Adds an image watermark to another image.

    Args:
        input_image_path (str): Path to the input image.
        output_image_path (str): Path to save the watermarked image.
        watermark_image_path (str): Path to the image file to use as a watermark.
                                    (Preferably a PNG with transparency).
        position (str): Placement of the watermark ("top-left", "top-right",
                        "bottom-left", "bottom-right", "center").
        scale_factor (float): Factor to scale the watermark image size
                              relative to the base image's width (e.g., 0.2 means 20% of base width).
        opacity (float): Opacity of the watermark (0.0 to 1.0).
        padding (int): Padding from the image edges.
    """
    try:
        base_img = Image.open(input_image_path).convert("RGBA")
        watermark_img = Image.open(watermark_image_path)
    except FileNotFoundError:
        print(f"Error: One or both image files not found ('{input_image_path}' or '{watermark_image_path}')")
        return
    except Exception as e:
        print(f"Error opening image(s): {e}")
        return

    # Resize watermark image based on scale_factor
    base_width, base_height = base_img.size
    watermark_width = int(base_width * scale_factor)
    watermark_height = int(watermark_width * watermark_img.height / watermark_img.width)
    watermark_img = watermark_img.resize((watermark_width, watermark_height), Image.Resampling.LANCZOS)

    # Apply opacity to the watermark image
    watermark_img = apply_image_opacity(watermark_img, opacity)

    # Calculate position for the watermark
    x, y = get_image_watermark_position(base_img.size, watermark_img.size, position, padding)

    # Paste the watermark onto the base image
    # The watermark_img itself acts as the mask due to its alpha channel
    base_img.paste(watermark_img, (x, y), watermark_img)

    # Save the output image
    try:
        # Convert to RGB before saving as JPEG to avoid issues with alpha channel
        if output_image_path.lower().endswith(('.jpg', '.jpeg')):
            base_img = base_img.convert("RGB")
        base_img.save(output_image_path)
        print(f"Image watermark added successfully. Saved to: {output_image_path}")
    except Exception as e:
        print(f"Error saving image to '{output_image_path}': {e}")


def main():
    parser = argparse.ArgumentParser(
        description="A simple image watermarking tool. Adds either text or another image as a watermark.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("input", help="Path to the input image file.")
    parser.add_argument("output", help="Path to save the output watermarked image file.")

    # Watermark type group
    watermark_group = parser.add_mutually_exclusive_group(required=True)
    watermark_group.add_argument("--text", type=str,
                                 help="Text to use as a watermark. (e.g., 'Copyright 2023')")
    watermark_group.add_argument("--image", type=str,
                                 help="Path to the image file to use as a watermark. (e.g., 'logo.png')")

    # Common options
    parser.add_argument("--position", type=str, default="bottom-right",
                        choices=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
                        help="Position of the watermark. (default: bottom-right)")
    parser.add_argument("--padding", type=int, default=20,
                        help="Padding from the image edges in pixels. (default: 20)")

    # Text watermark specific options
    parser.add_argument("--font", type=str, default="arial.ttf",
                        help="Path to the TrueType font file for text watermark. (e.g., 'arial.ttf'). "
                             "If not found, a default system font will be used.")
    parser.add_argument("--fontsize", type=int, default=40,
                        help="Font size for text watermark. (default: 40)")
    parser.add_argument("--textcolor", type=lambda s: tuple(map(int, s.split(','))),
                        default="0,0,0,128",
                        help="RGBA color for text watermark (e.g., '255,255,255,128' for semi-transparent white). "
                             "Default is '0,0,0,128' (semi-transparent black).")

    # Image watermark specific options
    parser.add_argument("--scale", type=float, default=0.2,
                        help="Scale factor for image watermark relative to the base image width. "
                             "(e.g., 0.2 for 20%% of base image width). (default: 0.2)")
    parser.add_argument("--opacity", type=float, default=0.5,
                        help="Opacity for image watermark (0.0 to 1.0, 1.0 is fully opaque). (default: 0.5)")

    args = parser.parse_args()

    # Determine which type of watermark to apply
    if args.text:
        add_text_watermark(
            input_image_path=args.input,
            output_image_path=args.output,
            watermark_text=args.text,
            font_path=args.font,
            font_size=args.fontsize,
            text_color=args.textcolor,
            position=args.position,
            padding=args.padding
        )
    elif args.image:
        add_image_watermark(
            input_image_path=args.input,
            output_image_path=args.output,
            watermark_image_path=args.image,
            position=args.position,
            scale_factor=args.scale,
            opacity=args.opacity,
            padding=args.padding
        )

if __name__ == "__main__":
    # --- Example Usage ---
    # This block demonstrates how to use the script programmatically or via command line.
    # It creates dummy images for testing purposes.

    print("--- Running Watermarking Tool Examples ---")

    # Create a dummy input image for testing
    dummy_input_image = "sample_input.jpg"
    img = Image.new('RGB', (800, 600), color = 'lightblue')
    d = ImageDraw.Draw(img)
    try:
        # Load a default font for the dummy text, or use Pillow's built-in if truetype fails
        try:
            # Common font paths vary by OS. Try Arial, fallback to default.
            # On Linux, 'FreeSans.ttf' or 'DejaVuSans.ttf' might work.
            # On macOS, 'Arial.ttf' or '/System/Library/Fonts/SFNSDisplay.ttf'
            font = ImageFont.truetype("arial.ttf", 50)
        except IOError:
            font = ImageFont.load_default()
            print("Note: 'arial.ttf' not found for dummy image, using default font.")

        d.text((50, 50), "Original Sample Image", fill=(0,0,0), font=font)
    except Exception as e:
        # Fallback if text drawing fails completely (e.g. no font could be loaded)
        d.text((50, 50), "Original Sample Image", fill=(0,0,0))
        print(f"Warning: Could not draw text with specific font for dummy image: {e}")

    img.save(dummy_input_image)
    print(f"Created dummy input image: {dummy_input_image}")

    # Create a dummy watermark image for testing
    dummy_watermark_image = "sample_logo.png"
    logo_img = Image.new('RGBA', (300, 150), color=(255, 0, 0, 100)) # Semi-transparent red background
    d_logo = ImageDraw.Draw(logo_img)
    try:
        # Using a smaller font for the dummy logo text
        try:
            font_logo = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font_logo = ImageFont.load_default()
            print("Note: 'arial.ttf' not found for dummy logo, using default font.")

        d_logo.text((20, 40), "My Logo", fill=(255, 255, 255, 255), font=font_logo)
    except Exception as e:
        d_logo.text((20, 40), "My Logo", fill=(255, 255, 255, 255))
        print(f"Warning: Could not draw text with specific font for dummy logo: {e}")

    logo_img.save(dummy_watermark_image)
    print(f"Created dummy watermark image: {dummy_watermark_image}\n")

    # --- Run text watermark example ---
    text_output_image = "output_text_watermark.jpg"
    print(f"Applying text watermark to {dummy_input_image}...")
    # You might need to adjust 'font_path' to a font available on your system.
    # Common fonts: "arial.ttf" (Windows), "DejaVuSans.ttf" or "FreeSans.ttf" (Linux),
    # "Arial.ttf" or "/System/Library/Fonts/SFNSDisplay.ttf" (macOS)
    add_text_watermark(
        input_image_path=dummy_input_image,
        output_image_path=text_output_image,
        watermark_text="CONFIDENTIAL - DO NOT DISTRIBUTE",
        font_path="arial.ttf", # Change this if 'arial.ttf' is not found on your system
        font_size=35,
        text_color=(255, 255, 255, 150), # Semi-transparent white
        position="center",
        padding=10
    )
    print(f"Check '{text_output_image}' for the result.\n")

    # --- Run image watermark example ---
    image_output_image = "output_image_watermark.png"
    print(f"Applying image watermark to {dummy_input_image}...")
    add_image_watermark(
        input_image_path=dummy_input_image,
        output_image_path=image_output_image,
        watermark_image_path=dummy_watermark_image,
        position="top-left",
        scale_factor=0.25, # Watermark will be 25% of the base image's width
        opacity=0.6,
        padding=30
    )
    print(f"Check '{image_output_image}' for the result.\n")

    # --- Clean up dummy files (optional) ---
    # Uncomment the following lines if you want to automatically remove the dummy files after execution
    # import os
    # os.remove(dummy_input_image)
    # os.remove(dummy_watermark_image)
    # print("Cleaned up dummy input and watermark images.")

    print("\n--- Command Line Usage Examples (run in your terminal) ---")
    print(f"To add text watermark (bottom-right, default font):")
    print(f"python {os.path.basename(__file__)} {dummy_input_image} cli_text_wm.jpg --text 'CLI Watermark' --textcolor '255,0,0,100'")
    print(f"\nTo add image watermark (center, scaled):")
    print(f"python {os.path.basename(__file__)} {dummy_input_image} cli_image_wm.png --image {dummy_watermark_image} --position center --scale 0.3 --opacity 0.7")
    print(f"\nExample with a different font (if available, e.g., 'times.ttf'):")
    print(f"python {os.path.basename(__file__)} {dummy_input_image} cli_font_wm.jpg --text 'Custom Font' --font 'times.ttf' --fontsize 50 --position bottom-left")

    # If you remove the dummy files above, you might want to recreate them for CLI examples
    # or ensure they exist before running the CLI commands.
    print("\nPlease run the command line examples manually in your terminal.")

    # Call main() function if you want to run the command line parser directly in __main__
    # For this example, we're demonstrating the functions directly and then showing CLI syntax.
    # main() # Uncomment this if you want to process args from command line directly from here.
