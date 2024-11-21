from logging import Logger
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from typing import Final
import subprocess
import tempfile
import os
import glob
import multiprocessing

from photos_previewer.logger import setup_logging

logger: Logger = setup_logging(logger_name=__name__)

#IMAGES_ROOT_DIR = os.path.expanduser('~/media/photos/2023')
#IMAGES_ROOT_DIR = os.path.expanduser('/mnt/icybox/media/photos/2022')
# BASE_FOLER_NAME: Final[str] = Path("/media/sda2/media/photos/")
IMAGES_ROOT_DIR = os.path.expanduser('/media/sda2/media/photos/2023')
FOLDER_PREFIX: str = '2023_'
"""Only choos folders with this prefix in the image root directory."""

OUTPUT = "preview_.jpg"
"""Final image is stored with this file name in current directory."""

##########################################
# TODO DNG IS NOT SUPPORTED, PLEASE FIX! #
##########################################
SUPPORTED_RAW_FILES: Final[str] = ['*.ARW', '*.CR2', '*.DNG']

def process_folder(folder: Path):
    for ext in SUPPORTED_RAW_FILES:
        images = glob.glob(os.path.join(str(folder), ext))
        if images:
            image_path = images[0]
            # TODO check if raw image have corresponding jpg, then just return that.
            if image_path.lower().endswith(".arw") or image_path.lower().endswith(".cr2"):
                # Convert raw image to a readable format using dcraw
                with tempfile.NamedTemporaryFile(suffix=".ppm") as temp_file:
                    subprocess.run(["dcraw", "-c", "-q", "3", image_path], stdout=temp_file)
                    img = Image.open(temp_file.name)
            else:
                img = Image.open(image_path)

            img.thumbnail((img.width // 8, img.height // 8))
            
            # Add label
            font_path = "/usr/share/fonts/liberation/LiberationSans-Regular.ttf"
            try:
                font = ImageFont.truetype(font_path, 40)
            except OSError:
                print(f"Warning: Couldn't load the TrueType font. Defaulting to built-in bitmap font.")
                font = ImageFont.load_default()

            draw = ImageDraw.Draw(img)
            #font = ImageFont.truetype("arial.ttf", 40)  # Use a font available on your system
            #draw.text((10,10), os.path.basename(folder), font=font)

            text = folder.name
            #text_width, text_height = draw.textsize(text, font=font)
            _, _, text_width, text_height = font.getbbox(text)

            box_x, box_y = 10, 10
            box_width = text_width + 20  # Add some padding
            box_height = text_height + 20  # Add some padding

            draw.rectangle([box_x, box_y, box_x + box_width, box_y + box_height], fill="gray")
            draw.text((box_x + 10, box_y + 10), text, font=font, fill="white")

            print(f"[x] {folder.name}")
                
            return img


def find_target_folders(images_root_dir: Path, folder_prefix: str | None = None) -> list[Path]:
    """Find target folders in the given root directory with an optional prefix.

    :param images_root_dir: Root directory to search for folders.
    :param folder_prefix: Optional prefix to filter folder names.
    :return: A sorted list of Path objects representing target folders.
    """
    target_folders: list[Path] = []
    for dir in images_root_dir.iterdir():
        if not dir.is_dir():
            continue
        if not folder_prefix or dir.name.startswith(folder_prefix):
            target_folders.append(dir)
    return list(sorted(target_folders))


def process(images_root_dir: Path, folder_prefix: str | None, output: Path):
    logger.info("Start process images folders ...")
    folders: list[Path] = find_target_folders(images_root_dir=images_root_dir, folder_prefix=folder_prefix)

    # Using a Pool of workers to process images in parallel
    with multiprocessing.Pool() as pool:
        images = pool.map(process_folder, folders)

    # Removing any None values (in case some folders didn't have images)
    images = list([img for img in images if img])

    logger.info(f"Concate {len(images)} images")

    if images:
        num_images = len(images)
        grid_size = int(num_images ** 0.5)
        num_rows = num_images // grid_size + (1 if num_images % grid_size else 0)

        combined_image = Image.new(
            'RGB', 
            (grid_size * images[0].width, num_rows * images[0].height)
        )
        for idx, img in enumerate(images):
            row = idx // grid_size
            col = idx % grid_size
            x = col * images[0].width
            y = row * images[0].height
            combined_image.paste(img, (x, y))
        
        combined_image.save(output)
