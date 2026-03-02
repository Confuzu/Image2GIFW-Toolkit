import os
import argparse
from PIL import Image
from collections import defaultdict
import re
import logging

from logging_config import setup_logging

logger_imagetogif = logging.getLogger('image2gifw.imagetogif')

def remove_common_parts(filename):
    # Remove file extension
    filename = os.path.splitext(filename)[0]
    # Remove common terms like 'safetensors'
    common_terms = ['safetensors', 'XL']
    for term in common_terms:
        filename = filename.replace(term, '')
    # Only strip digits if the filename contains alphabetic characters
    # (model-name files like "CoolModel_v2"). For numeric-only filenames
    # (e.g. SD image outputs "00425-2068717781-0000"), digits are the
    # meaningful identifiers and must be preserved.
    if re.search(r'[a-zA-Z]', filename):
        filename = re.sub(r'[\d_]', '', filename)
    else:
        filename = re.sub(r'_', '-', filename)
    return filename.strip('-_ ')

def find_longest_common_substring(str1, str2):
    """Find the longest common substring using dynamic programming. O(n*m)."""
    if not str1 or not str2:
        return ""
    m, n = len(str1), len(str2)
    prev = [0] * (n + 1)
    best_len = 0
    best_end = 0
    for i in range(1, m + 1):
        curr = [0] * (n + 1)
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                curr[j] = prev[j - 1] + 1
                if curr[j] > best_len:
                    best_len = curr[j]
                    best_end = i
        prev = curr
    return str1[best_end - best_len:best_end]


def find_common_substrings(filenames):
    """Find the longest common substring across all filenames. Returns a list for compatibility."""
    if not filenames:
        return []

    cleaned_filenames = [remove_common_parts(f) for f in filenames]
    result = cleaned_filenames[0]
    for filename in cleaned_filenames[1:]:
        result = find_longest_common_substring(result, filename)
        if not result:
            return []

    return [result] if len(result) > 3 else []


def group_images_by_substring(image_files):
    groups = defaultdict(list)
    for file in image_files:
        cleaned_file = remove_common_parts(file)
        best_key = None
        best_lcs_len = 0
        for key in groups.keys():
            cleaned_key = remove_common_parts(key)
            lcs = find_longest_common_substring(cleaned_key, cleaned_file)
            if len(lcs) > best_lcs_len:
                best_lcs_len = len(lcs)
                best_key = key
        # Use a proportional threshold: LCS must exceed 1/3 of the shorter
        # filename length (min 4 chars). This prevents grouping on short
        # coincidental matches like common suffixes.
        min_len = min(len(cleaned_file), len(remove_common_parts(best_key))) if best_key else 0
        threshold = max(3, min_len // 3)
        if best_key and best_lcs_len > threshold:
            groups[best_key].append(file)
        else:
            groups[file] = [file]
    return groups

def create_gifs_from_folder(image_folder, output_folder, group_size=None, duration=1.0, recursive=False, filename_pattern=None):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logger_imagetogif.info(f"Created output folder: {output_folder}")

    def create_gif(image_files, output_path):
        try:
            images = []
            target_size = None
            for file_name in image_files:
                file_path = os.path.join(root, file_name)
                image = Image.open(file_path)
                if target_size is None:
                    target_size = image.size
                image = image.resize(target_size, Image.Resampling.LANCZOS)
                images.append(image)
            
            if images:
                images[0].save(output_path, save_all=True, append_images=images[1:], duration=duration, loop=0)
                logger_imagetogif.info(f'GIF created: {output_path}')
                print(f'GIF created: {output_path}')
            else:
                logger_imagetogif.warning(f'No images to create GIF in {root}')
        except Exception as e:
            logger_imagetogif.error(f'Error creating GIF in {root}: {e}')
            print(f'Error creating GIF in {root}: {e}')

    def filter_images_by_pattern(image_files, pattern):
        return [f for f in image_files if pattern.lower() in f.lower()]

    try:
        for root, dirs, files in os.walk(image_folder):
            image_files = sorted([f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
            
            if not image_files:
                logger_imagetogif.warning(f'No images found in {root}, skipping...')
                print(f'No images found in {root}, skipping...')
                continue
            
            if filename_pattern:
                image_files = filter_images_by_pattern(image_files, filename_pattern)
                if not image_files:
                    logger_imagetogif.warning(f'No images matching pattern "{filename_pattern}" found in {root}, skipping...')
                    print(f'No images matching pattern "{filename_pattern}" found in {root}, skipping...')
                    continue
            
            if group_size is None or group_size <= 0:
                # Group images by common substrings in the filename
                image_groups = group_images_by_substring(image_files)
                for base_name, group in image_groups.items():
                    if len(group) > 1:  # Only create GIFs for groups with more than one image
                        common_substrings = find_common_substrings(group)
                        name_part = common_substrings[0].strip('-_ ') if common_substrings else 'group'
                        gif_name = f"{name_part}.gif"
                        output_path = os.path.join(output_folder, gif_name)
                        create_gif(group, output_path)
            else:
                for i in range(0, len(image_files), group_size):
                    group = image_files[i:i + group_size]
                    if len(group) > 1:
                        base_name = os.path.splitext(group[0])[0]
                        gif_name = f"{base_name}_{i//group_size+1}.gif"
                        output_path = os.path.join(output_folder, gif_name)
                        create_gif(group, output_path)
            
            if not recursive:
                break

        logger_imagetogif.info("GIF creation process completed successfully.")
        print("GIF creation process completed successfully.")
    except Exception as e:
        logger_imagetogif.error(f"An error occurred during GIF creation: {str(e)}")
        print(f"An error occurred during GIF creation: {str(e)}")

if __name__ == "__main__":
    setup_logging()
    parser = argparse.ArgumentParser(description='Create GIFs from image sequences')
    parser.add_argument('image_folder', help='Folder containing images')
    parser.add_argument('-o', '--output', default=None, help='Output folder (default: same as image folder)')
    parser.add_argument('-g', '--group-size', type=int, default=None, help='Number of images per GIF (default: group by common substrings)')
    parser.add_argument('-d', '--duration', type=float, default=1.0, help='Duration per frame in seconds (default: 1.0)')
    parser.add_argument('-r', '--recursive', action='store_true', help='Search in subfolders')
    parser.add_argument('-p', '--pattern', default=None, help='Filename pattern to match')

    args = parser.parse_args()
    output_folder = args.output if args.output else args.image_folder
    duration_ms = args.duration * 1000.0

    try:
        create_gifs_from_folder(args.image_folder, output_folder, group_size=args.group_size, duration=duration_ms, recursive=args.recursive, filename_pattern=args.pattern)
    except Exception as e:
        logger_imagetogif.error(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")
