import os
import sys
import argparse
import logging
from logging_config import setup_logging
from imagetogif import create_gifs_from_folder
from gif_rename_with_model_name import rename_gifs, rename_gifs_with_confirmation, rename_gifs_dry_run
from wildcard_creator import list_model_files

setup_logging()
logger = logging.getLogger('image2gifw.main')

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
        logger.info("Image to GIF conversion completed successfully.")
    except ValueError as ve:
        logger.error(f"Invalid input in Image to GIF conversion: {ve}")
        print(f"Invalid input: {ve}")
    except Exception as e:
        logger.error(f"Error in image to GIF conversion: {str(e)}")
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

        logger.info("GIF renaming completed successfully.")
    except ValueError as ve:
        logger.error(f"Invalid input in GIF renaming: {ve}")
        print(f"Invalid input: {ve}")
    except Exception as e:
        logger.error(f"Error in GIF renaming: {str(e)}")
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
        logger.info(f"Wildcard creator completed successfully. Output file: {output_file_name}")
        print(f"Wildcard list created: {output_file_name}")
    except Exception as e:
        logger.error(f"Error in wildcard creator: {str(e)}")
        print(f"An error occurred: {str(e)}")

def interactive_menu():
    while True:
        print("\nImage2GIFW Toolkit Menu:")
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
                logger.info("Program exited normally.")
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")
                logger.warning(f"Invalid menu choice: {choice}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            logger.error(f"Unexpected error in main menu: {str(e)}")


def cmd_gif(args):
    output_folder = args.output if args.output else args.image_folder
    duration_ms = args.duration * 1000.0
    create_gifs_from_folder(args.image_folder, output_folder, group_size=args.group_size,
                            duration=duration_ms, recursive=args.recursive, filename_pattern=args.pattern)


def cmd_rename(args):
    if args.mode == 'normal':
        rename_gifs(args.image_folder, args.min_length)
    elif args.mode == 'confirm':
        rename_gifs_with_confirmation(args.image_folder, args.min_length)
    elif args.mode == 'dry-run':
        rename_gifs_dry_run(args.image_folder, args.min_length)


def cmd_wildcard(args):
    list_model_files(args.image_folder, args.output)


def main():
    parser = argparse.ArgumentParser(description='Image2GIFW Toolkit - GIF creation, renaming, and wildcard utilities')
    subparsers = parser.add_subparsers(dest='command')

    # gif subcommand
    gif_parser = subparsers.add_parser('gif', help='Create GIFs from image sequences')
    gif_parser.add_argument('image_folder', help='Folder containing images')
    gif_parser.add_argument('-o', '--output', default=None, help='Output folder (default: same as image folder)')
    gif_parser.add_argument('-g', '--group-size', type=int, default=None, help='Images per GIF (default: group by common substrings)')
    gif_parser.add_argument('-d', '--duration', type=float, default=1.0, help='Duration per frame in seconds (default: 1.0)')
    gif_parser.add_argument('-r', '--recursive', action='store_true', help='Search in subfolders')
    gif_parser.add_argument('-p', '--pattern', default=None, help='Filename pattern to match')
    gif_parser.set_defaults(func=cmd_gif)

    # rename subcommand
    rename_parser = subparsers.add_parser('rename', help='Rename GIFs based on model filenames')
    rename_parser.add_argument('image_folder', help='Folder containing GIF and model files')
    rename_parser.add_argument('-m', '--min-length', type=int, default=4, help='Minimum common substring length (default: 4)')
    rename_parser.add_argument('--mode', choices=['normal', 'confirm', 'dry-run'], default='normal', help='Rename mode (default: normal)')
    rename_parser.set_defaults(func=cmd_rename)

    # wildcard subcommand
    wildcard_parser = subparsers.add_parser('wildcard', help='Create wildcard list of model filenames')
    wildcard_parser.add_argument('image_folder', help='Folder to search for .pt and .safetensors files')
    wildcard_parser.add_argument('-o', '--output', default='model_files.txt', help='Output filename (default: model_files.txt)')
    wildcard_parser.set_defaults(func=cmd_wildcard)

    args = parser.parse_args()

    if args.command is None:
        # No subcommand given, fall back to interactive menu
        interactive_menu()
    else:
        args.func(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting.")
        logger.info("Program interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        logger.critical(f"Critical error in main program: {str(e)}")
