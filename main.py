import os
import sys
import logging
from imagetogif import create_gifs_from_folder
from gif_rename_with_model_name import rename_gifs, rename_gifs_with_confirmation, rename_gifs_dry_run
from wildcard_creator import list_model_files

script_dir = os.path.dirname(os.path.abspath(__file__))

# Set up logging
logging.basicConfig(filename=os.path.join(script_dir, 'merged_project.log'), 
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8')

# Global variable to store the last used directory
last_used_directory = ""

def get_directory_input(prompt):
    global last_used_directory
    if last_used_directory:
        user_input = input(f"{prompt} (Press Enter to use '{last_used_directory}'): ")
        if not user_input:
            return last_used_directory
    else:
        user_input = input(f"{prompt}: ")
    
    last_used_directory = user_input
    return user_input

def run_image_to_gif():
    try:
        image_folder = get_directory_input('Please enter the image folder')
        output_folder = input('Please input the output folder (press Enter to use the same as image folder): ')
        if not output_folder:
            output_folder = image_folder
        group_size = input('Enter group size, number of images per GIF (press Enter to group by common substrings): ')
        duration = input('Duration per frame in seconds (press Enter for default 1000 ms = 1 seconds): ')
        recursive = input('Search in subfolders as well? (yes or no): ').strip().lower() == 'yes'
        filename_pattern = input('Enter filename pattern to match (optional, press Enter to skip): ')

        group_size = int(group_size) if group_size else None
        duration = float(duration) * 1000.0 if duration else 1000.0

        create_gifs_from_folder(image_folder, output_folder, group_size=group_size, duration=duration, recursive=recursive, filename_pattern=filename_pattern)
        logging.info("Image to GIF conversion completed successfully.")
    except ValueError as ve:
        logging.error(f"Invalid input in Image to GIF conversion: {ve}")
        print(f"Invalid input: {ve}")
    except Exception as e:
        logging.error(f"Error in image to GIF conversion: {str(e)}")
        print(f"An error occurred: {str(e)}")

def run_gif_rename():
    try:
        image_folder = get_directory_input('Please enter the image folder')
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
            print("Invalid mode selected. Operation cancelled.")
            return
        
        logging.info("GIF renaming completed successfully.")
    except ValueError as ve:
        logging.error(f"Invalid input in GIF renaming: {ve}")
        print(f"Invalid input: {ve}")
    except Exception as e:
        logging.error(f"Error in GIF renaming: {str(e)}")
        print(f"An error occurred: {str(e)}")

def run_wildcard_creator():
    try:
        image_folder = get_directory_input('Please enter the image folder')
        
        # Find the first .pt or .safetensors file in the directory
        model_files = [f for f in os.listdir(image_folder) if f.endswith(('.pt', '.safetensors'))]
        default_name = model_files[0].rsplit('.', 1)[0] + '.txt' if model_files else "model_files.txt"
        
        output_file_name = input(f'Please enter the output file name (press Enter to use "{default_name}"): ')
        if not output_file_name:
            output_file_name = default_name
        
        list_model_files(image_folder, output_file_name)
        logging.info(f"Wildcard creator completed successfully. Output file: {output_file_name}")
        print(f"Wildcard list created: {output_file_name}")
    except Exception as e:
        logging.error(f"Error in wildcard creator: {str(e)}")
        print(f"An error occurred: {str(e)}")

def main():
    while True:
        print("\nMerged Project Menu:")
        print("1. Create GIFs from images")
        print("2. Rename GIFs based on .pt and .safetensors files")
        print("3. Create wildcard list of .pt and .safetensors files")
        print("4. Run all scripts in sequence")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        try:
            if choice == '1':
                run_image_to_gif()
            elif choice == '2':
                run_gif_rename()
            elif choice == '3':
                run_wildcard_creator()
            elif choice == '4':
                print("Running all scripts in sequence...")
                run_image_to_gif()
                run_gif_rename()
                run_wildcard_creator()
            elif choice == '5':
                print("Exiting the program. Goodbye!")
                logging.info("Program exited normally.")
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")
                logging.warning(f"Invalid menu choice: {choice}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            logging.error(f"Unexpected error in main menu: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting.")
        logging.info("Program interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        logging.critical(f"Critical error in main program: {str(e)}")