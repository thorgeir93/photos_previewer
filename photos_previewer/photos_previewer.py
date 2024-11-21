from pathlib import Path

import click
from logging import Logger

from photos_previewer.generate_preview import process, find_target_folders
from photos_previewer.logger import setup_logging, verbose_to_log_level

logger: Logger = setup_logging(logger_name=__name__)

DEFAULT_OUTPUT_DIR: Path = Path("./previews/")

def click_verbose_to_log_level(ctx, param, value) -> int:
    """Translate the verbosity count to logging levels.

    :param ctx: Click context (not used here).
    :param param: The parameter being processed (not used here).
    :param value: The verbosity count.
    :return: The corresponding logging level constant.
    """
    return verbose_to_log_level(value)

@click.command()
@click.option(
    '--images-root-dir',
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Root directory containing image folders.",
)
@click.option(
    '--folder-prefix',
    default=None,
    type=str,
    help="Prefix for folders to process if need. "
    "Used to narrow down the target folders in the given root dir.",
)
@click.option(
    '--output',
    default=None,
    type=click.Path(path_type=Path),
    help="Output file name for the preview image. "
    "By default the image root dir name will be used.",
)
@click.option(
    '-v', '--verbose',
    count=True,
    type=int,
    callback=click_verbose_to_log_level,
    default=0,
    help="Increase verbosity (e.g., -v, -vv for DEBUG level).",
)
def cli(images_root_dir: Path, folder_prefix: str | None, output: Path | None, verbose: int):
    """Generate a preview image by processing folders of images in the specified root directory.
    """
    logger.setLevel(verbose)

    logger.info(f"Received input parameters:")
    logger.info(f"  Images root directory: {images_root_dir}")
    logger.info(f"  Folder prefix: {folder_prefix if folder_prefix else 'None'}")
    logger.info(f"  Verbosity level: {verbose}")

    if not output:
        DEFAULT_OUTPUT_DIR.mkdir(exist_ok=True)
        images_root_dir_str: str = str(images_root_dir)
        output = DEFAULT_OUTPUT_DIR / f"{images_root_dir_str.strip('/').replace('/', '_')}_preview.jpg"
        logger.info(f"  Output not provided; defaulting to: {output}")
    else:
        logger.info(f"  Output file: {output}")

    folders: list[Path] = find_target_folders(images_root_dir=images_root_dir, folder_prefix=folder_prefix)
    logger.info(f"Number target folders are {len(folders)}")
    logger.debug(f"Target folders: {"\n".join([dir.name for dir in folders])}")
    process(images_root_dir, folder_prefix, output)

if __name__ == '__main__':
    cli()