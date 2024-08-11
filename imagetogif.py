import os
import imageio.v3 as iio
from PIL import Image
from collections import defaultdict
import re
import logging

script_dir = os.path.dirname(os.path.abspath(__file__))

# Configure logger for imagetogif_V1.py
logger_imagetogif = logging.getLogger('imagetogif')
logger_imagetogif.setLevel(logging.DEBUG)

# Add file handler
log_file_path = os.path.join(script_dir, "process_log_imagetogif.txt")
file_handler_imagetogif = logging.FileHandler(log_file_path, encoding='utf-8')
file_handler_imagetogif.setLevel(logging.DEBUG)

# Add format handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler_imagetogif.setFormatter(formatter)

# Add handler to the logger
logger_imagetogif.addHandler(file_handler_imagetogif)

def remove_common_parts(filename):
    # Remove file extension
    filename = os.path.splitext(filename)[0]
    # Remove common terms like 'safetensors'
    common_terms = ['safetensors', 'XL']
    for term in common_terms:
        filename = filename.replace(term, '')
    # Remove numbers and underscores
    filename = re.sub(r'[\d_]', '', filename)
    return filename.strip()

def find_common_substrings(filenames):
    def get_substrings(s):
        return set(s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1) if len(s[i:j]) > 3)

    if not filenames:
        return []

    cleaned_filenames = [remove_common_parts(f) for f in filenames]
    common_substrings = get_substrings(cleaned_filenames[0])
    for filename in cleaned_filenames[1:]:
        common_substrings &= get_substrings(filename)

    return sorted(common_substrings, key=len, reverse=True)
def group_images_by_substring(image_files):
    groups = defaultdict(list)
    for file in image_files:
        grouped = False
        cleaned_file = remove_common_parts(file)
        for key in groups.keys():
            cleaned_key = remove_common_parts(key)
            if any(substr in cleaned_file and substr in cleaned_key 
                   for substr in find_common_substrings([cleaned_key, cleaned_file])):
                groups[key].append(file)
                grouped = True
                break
        if not grouped:
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
                        gif_name = f"{common_substrings[0] if common_substrings else 'group'}.gif"
                        gif_name = gif_name.replace('..', '.')  # Remove any double dots
                        output_path = os.path.join(output_folder, gif_name)
                        create_gif(group, output_path)
            else:
                for i in range(0, len(image_files), group_size):
                    group = image_files[i:i + group_size]
                    if len(group) == group_size:
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
    try:
        image_folder = input('Enter the image folder: ')
        output_folder = input('Enter the output folder (press Enter to use the same as image folder): ')
        if not output_folder:
            output_folder = image_folder
        group_size = input('Enter group size number of images per GIF (press Enter to group by common substrings): ')
        duration = input('Duration per frame in seconds (press Enter for default 1000 ms = 1 seconds): ')
        recursive = input('Search in subfolders? (yes/no): ').strip().lower() == 'yes'
        filename_pattern = input('Enter filename pattern to match (optional, press Enter to skip): ')

        group_size = int(group_size) if group_size else None
        duration = float(duration) * 1000.0 if duration else 1000.0

        create_gifs_from_folder(image_folder, output_folder, group_size=group_size, duration=duration, recursive=recursive, filename_pattern=filename_pattern)
    except ValueError as ve:
        logger_imagetogif.error(f"Invalid input: {ve}")
        print(f"Invalid input: {ve}")
    except Exception as e:
        logger_imagetogif.error(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")