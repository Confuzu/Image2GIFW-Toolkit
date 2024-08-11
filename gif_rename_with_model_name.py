import os
import logging

# Changes and explanations:
# The rename_gifs function takes an additional parameter min_substring_length with a default value of 4.

# A smaller value (e.g., 2 or 3) will allow for more liberal matching, 
# potentially catching more files but also increasing the risk of false matches.

# A larger value (e.g., 5 or 6) will require a longer common substring, 
# reducing the chance of false matches but potentially missing some files that should be renamed.

import os
import logging

script_dir = os.path.dirname(os.path.abspath(__file__))

# Configure logger for gif_rename_with_model_name.py
logger_gif_rename = logging.getLogger('gif_rename')
logger_gif_rename.setLevel(logging.DEBUG)

# Add file handler
log_file_path = os.path.join(script_dir, "process_log_gif_rename.txt")
file_handler_gif_rename = logging.FileHandler(log_file_path, encoding='utf-8')
file_handler_gif_rename.setLevel(logging.DEBUG)

# Add format handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler_gif_rename.setFormatter(formatter)

# Add handler to the logger
logger_gif_rename.addHandler(file_handler_gif_rename)

def find_common_substring(str1, str2):
    str1 = str1.lower()
    str2 = str2.lower()
    s1 = set(str1[i:j] for i in range(len(str1)) for j in range(i + 1, len(str1) + 1))
    s2 = set(str2[i:j] for i in range(len(str2)) for j in range(i + 1, len(str2) + 1))
    common = s1 & s2
    return max(common, key=len, default="") if common else ""

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
    image_folder = input('Enter the image folder: ')
    min_substring_length = input('Enter the minimum common substring length (press Enter for default 4): ')
    min_substring_length = int(min_substring_length) if min_substring_length else 4
    
    mode = input('Choose mode (1: Normal, 2: With Confirmation, 3: Dry Run): ')
    
    if mode == '1':
        rename_gifs(image_folder, min_substring_length)
    elif mode == '2':
        rename_gifs_with_confirmation(image_folder, min_substring_length)
    elif mode == '3':
        rename_gifs_dry_run(image_folder, min_substring_length)
    else:
        print("Invalid mode selected. Exiting.")