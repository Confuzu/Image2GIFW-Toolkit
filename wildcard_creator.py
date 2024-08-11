import os
import logging

script_dir = os.path.dirname(os.path.abspath(__file__))

# Configure logger for wildcard_creator.py
logger_wildcard = logging.getLogger('wildcard_creator')
logger_wildcard.setLevel(logging.DEBUG)

# Add file handler
log_file_path = os.path.join(script_dir, "process_log_wildcard_creator.txt")
file_handler_wildcard = logging.FileHandler(log_file_path, encoding='utf-8')
file_handler_wildcard.setLevel(logging.DEBUG)

# Add format handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler_wildcard.setFormatter(formatter)

# Add handler to the logger
logger_wildcard.addHandler(file_handler_wildcard)

def list_model_files(image_folder, output_file):
    model_files = []
    
    try:
        # Search the folder and subfolders
        for root, dirs, files in os.walk(image_folder):
            for file in files:
                if file.endswith(('.pt', '.safetensors')):
                    model_files.append(os.path.splitext(file)[0])
        
        # If output_file is empty or not provided, use a default name
        if not output_file:
            output_file = "model_files.txt"
        
        # Ensure output_file is a file name, not just a directory
        if os.path.isdir(output_file):
            output_file = os.path.join(output_file, "model_files.txt")
        
        output_file = os.path.join(script_dir, output_file)

        # Write the file names to the text file
        with open(output_file, 'w', encoding='utf-8') as f:
            for model_file in model_files:
                f.write(model_file + '\n')
        
        logger_wildcard.info(f'{len(model_files)} .pt and .safetensors files found and written to {output_file}.')
        print(f'{len(model_files)} .pt and .safetensors files found and written to {output_file}.')
    except PermissionError:
        error_msg = f"Permission denied when accessing {image_folder} or writing to {output_file}"
        logger_wildcard.error(error_msg)
        print(f"Error: {error_msg}")
    except IOError as e:
        error_msg = f"I/O error({e.errno}): {e.strerror}"
        logger_wildcard.error(error_msg)
        print(f"Error: {error_msg}")
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger_wildcard.error(error_msg)
        print(f"Error: {error_msg}")

if __name__ == "__main__":
    try:
        image_folder = input('Please enter the image folder: ')
        output_file_name = input('Please enter the output file name (press Enter to use default "model_files.txt"): ')
        list_model_files(image_folder, output_file_name)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        logger_wildcard.info("Operation cancelled by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logger_wildcard.error(f"An unexpected error occurred: {e}")