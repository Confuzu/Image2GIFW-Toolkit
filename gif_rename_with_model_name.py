import os
import logging

from logging_config import setup_logging

# The rename_gifs function takes an additional parameter min_substring_length with a default value of 4.
#
# A smaller value (e.g., 2 or 3) will allow for more liberal matching,
# potentially catching more files but also increasing the risk of false matches.
#
# A larger value (e.g., 5 or 6) will require a longer common substring,
# reducing the chance of false matches but potentially missing some files that should be renamed.

logger_gif_rename = logging.getLogger('image2gifw.gif_rename')

def find_common_substring(str1, str2):
    """Find the longest common substring using dynamic programming. O(n*m)."""
    str1 = str1.lower()
    str2 = str2.lower()
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

def rename_gifs(image_folder, min_substring_length=4):
    for root, dirs, files in os.walk(image_folder):
        model_files = [f for f in files if f.endswith(('.pt', '.safetensors'))]
        gif_files = [f for f in files if f.endswith('.gif')]

        if not model_files:
            logger_gif_rename.warning(f'No .pt or .safetensors files found in {root}, skipping...')
            continue

        if not gif_files:
            logger_gif_rename.warning(f'No .gif files found in {root}, skipping...')
            continue

        for gif_file in gif_files:
            gif_base_name = os.path.splitext(gif_file)[0]
            best_match = None
            best_match_length = 0
            for model_file in model_files:
                model_base_name = os.path.splitext(model_file)[0]
                common = find_common_substring(model_base_name, gif_base_name)
                
                if len(common) >= min_substring_length:
                    match_quality = len(common) / len(model_base_name)
                    if match_quality > best_match_length:
                        best_match = model_base_name
                        best_match_length = match_quality

            if best_match:
                old_path = os.path.join(root, gif_file)
                new_name = f"{best_match}.gif"
                new_path = os.path.join(root, new_name)
                if old_path != new_path:
                    try:
                        if os.path.exists(new_path):
                            logger_gif_rename.warning(f'Warning: {new_name} already exists in {root}, skipping...')
                        else:
                            os.rename(old_path, new_path)
                            logger_gif_rename.info(f'Renamed {gif_file} to {new_name} in {root}')
                            print(f'Renamed {gif_file} to {new_name} in {root}')
                    except PermissionError:
                        logger_gif_rename.error(f'Permission denied when renaming {gif_file} in {root}')
                        print(f'Error: Permission denied when renaming {gif_file}')
                    except OSError as e:
                        logger_gif_rename.error(f'OS error when renaming {gif_file} in {root}: {e}')
                        print(f'Error: OS error when renaming {gif_file}: {e}')
                    except Exception as e:
                        logger_gif_rename.error(f'Unexpected error when renaming {gif_file} in {root}: {e}')
                        print(f'Error: Unexpected error when renaming {gif_file}: {e}')

def rename_gifs_with_confirmation(image_folder, min_substring_length=4):
    changes = {}
    for root, dirs, files in os.walk(image_folder):
        model_files = [f for f in files if f.endswith(('.pt', '.safetensors'))]
        gif_files = [f for f in files if f.endswith('.gif')]

        if not model_files or not gif_files:
            continue

        for gif_file in gif_files:
            gif_base_name = os.path.splitext(gif_file)[0]
            best_match = None
            best_match_length = 0
            for model_file in model_files:
                model_base_name = os.path.splitext(model_file)[0]
                common = find_common_substring(model_base_name, gif_base_name)
                
                if len(common) >= min_substring_length:
                    match_quality = len(common) / len(model_base_name)
                    if match_quality > best_match_length:
                        best_match = model_base_name
                        best_match_length = match_quality

            if best_match:
                old_path = os.path.join(root, gif_file)
                new_name = f"{best_match}.gif"
                new_path = os.path.join(root, new_name)
                if old_path != new_path and old_path not in changes:
                    changes[old_path] = new_path

    if changes:
        print("The following changes will be made:")
        for old, new in changes.items():
            print(f"Rename: {os.path.basename(old)} -> {os.path.basename(new)}")
        
        confirm = input("Do you want to proceed with these changes? (y/n): ").lower()
        if confirm == 'y':
            for old_path, new_path in changes.items():
                try:
                    if os.path.exists(new_path):
                        logger_gif_rename.warning(f'Warning: {os.path.basename(new_path)} already exists, skipping...')
                        print(f'Warning: {os.path.basename(new_path)} already exists, skipping...')
                    else:
                        os.rename(old_path, new_path)
                        logger_gif_rename.info(f'Renamed {os.path.basename(old_path)} to {os.path.basename(new_path)}')
                        print(f'Renamed {os.path.basename(old_path)} to {os.path.basename(new_path)}')
                except PermissionError:
                    logger_gif_rename.error(f'Permission denied when renaming {os.path.basename(old_path)}')
                    print(f'Error: Permission denied when renaming {os.path.basename(old_path)}')
                except OSError as e:
                    logger_gif_rename.error(f'OS error when renaming {os.path.basename(old_path)}: {e}')
                    print(f'Error: OS error when renaming {os.path.basename(old_path)}: {e}')
                except Exception as e:
                    logger_gif_rename.error(f'Unexpected error when renaming {os.path.basename(old_path)}: {e}')
                    print(f'Error: Unexpected error when renaming {os.path.basename(old_path)}: {e}')
        else:
            print("Operation cancelled.")
            logger_gif_rename.info("Renaming operation cancelled by user.")
    else:
        print("No changes to make.")
        logger_gif_rename.info("No changes to make in the renaming operation.")

def rename_gifs_dry_run(image_folder, min_substring_length=4):
    changes = {}
    for root, dirs, files in os.walk(image_folder):
        model_files = [f for f in files if f.endswith(('.pt', '.safetensors'))]
        gif_files = [f for f in files if f.endswith('.gif')]

        if not model_files or not gif_files:
            continue

        for gif_file in gif_files:
            gif_base_name = os.path.splitext(gif_file)[0]
            best_match = None
            best_match_length = 0
            for model_file in model_files:
                model_base_name = os.path.splitext(model_file)[0]
                common = find_common_substring(model_base_name, gif_base_name)
                
                if len(common) >= min_substring_length:
                    match_quality = len(common) / len(model_base_name)
                    if match_quality > best_match_length:
                        best_match = model_base_name
                        best_match_length = match_quality

            if best_match:
                old_path = os.path.join(root, gif_file)
                new_name = f"{best_match}.gif"
                new_path = os.path.join(root, new_name)
                if old_path != new_path and old_path not in changes:
                    changes[old_path] = new_path

    if changes:
        print("The following changes would be made in a real run:")
        for old, new in changes.items():
            print(f"Rename: {os.path.basename(old)} -> {os.path.basename(new)}")
            logger_gif_rename.info(f"Would rename {os.path.basename(old)} -> {os.path.basename(new)}")
    else:
        print("No changes would be made.")

    logger_gif_rename.info(f"Dry run completed. {len(changes)} potential changes identified.")

if __name__ == "__main__":
    import argparse
    setup_logging()
    parser = argparse.ArgumentParser(description='Rename GIF files based on matching model filenames')
    parser.add_argument('image_folder', help='Folder containing GIF and model files')
    parser.add_argument('-m', '--min-length', type=int, default=4, help='Minimum common substring length (default: 4)')
    parser.add_argument('--mode', choices=['normal', 'confirm', 'dry-run'], default='normal',
                        help='Rename mode (default: normal)')

    args = parser.parse_args()

    if args.mode == 'normal':
        rename_gifs(args.image_folder, args.min_length)
    elif args.mode == 'confirm':
        rename_gifs_with_confirmation(args.image_folder, args.min_length)
    elif args.mode == 'dry-run':
        rename_gifs_dry_run(args.image_folder, args.min_length)
