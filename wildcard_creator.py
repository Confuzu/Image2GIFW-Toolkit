import os
import logging

from logging_config import setup_logging

script_dir = os.path.dirname(os.path.abspath(__file__))

logger_wildcard = logging.getLogger('image2gifw.wildcard')

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

        # Sanitize: strip path components to prevent path traversal
        output_file = os.path.basename(output_file)
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
    import argparse
    setup_logging()
    parser = argparse.ArgumentParser(description='Create wildcard list of model filenames')
    parser.add_argument('image_folder', help='Folder to search for .pt and .safetensors files')
    parser.add_argument('-o', '--output', default='model_files.txt', help='Output filename (default: model_files.txt)')

    args = parser.parse_args()
    list_model_files(args.image_folder, args.output)
