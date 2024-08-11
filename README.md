#### Image2GIFW-Toolkit

#### WHY? 
My goal with this project was to create GIFs for Loras, embedings, and models. I felt that a single image doesn't always show what a model is capable of. However, creating GIFs manually is pretty tedious and monotonous, so I thought I'd try to automate it to a certain extent. The result is the Project Image2GIFW toolkit, which could be a very good addition to my other project, CivitAI-Model-grabber. 
What i also added in the course of the development is the wildcard creation which simply creates a txt file with the names of the .pt or safetensors files. 


It consists of three primary scripts that provide the following functionalities:

- **Simplify GIF Creation**: Easily convert image sequences into GIFs with customizable options.
    For the dimensions of the gif, the values of the first image that is processed are used. target size = image size. 
    The images that do not fit are adjusted with Resampling.LANCZOS
  
- **Efficient File Management**: Rename GIFs to align with corresponding model files, for better organization and accessibility.
    

- **Wildcard Functionality**: Creates a txt File with the names of the .pt or .safetensors files to use is as a wildcard txt file.

### Installation

#### System Requirements

- **Python Version**: Ensure Python 3.6 or higher is installed on your system.
- **Operating System**: Compatible with Windows, macOS, and Linux.

#### Installation Steps

1. **Clone the Repository**:
    - Ensure all script files (`main.py`, `imagetogif.py`, `gif_rename_with_model_name.py`, `wildcard_creator.py`) are in the same directory.
     ```
     pip install Pillow imageio
     ```

3. **Set Up Directories**:
   - Place all image and model files in the directories you plan to use.
   - Ensure write permissions for the directories where you want to save output files.

### Usage

#### Main Interface (`main.py`)

The main script provides a unified interface to access all functionalities of the project. Run it using the command:

```
python main.py
```

You will be presented with the following options:

1. **Create GIFs from images**: Use this option to convert image sequences into GIFs.
2. **Rename GIFs based on .pt and .safetensors files**: This option helps rename GIF files according to corresponding model files.
3. **Create wildcard list of .pt and .safetensors files**: Generates a list of model files in the specified directory.
4. **Run all scripts in sequence**: Executes all available functionalities one after another.
5. **Exit**: Close the application.

#### Additional Features

- **Last Used Directory**: The scripts remember the last directory used for convenience.
- **Logging**: Each script creates a log file in the script directory with detailed execution information.
- **Error Handling**: Comprehensive error handling with user-friendly messages and detailed logging.

##### Single Script Usage 

#### 1. Image to GIF Creator (`imagetogif.py`)

This script converts image sequences into GIFs with various configurable options.

##### Options:
- **Image folder**: Specify the directory containing the images.
- **Output folder**: Define where to save the resulting GIFs (default is the same as the image folder).
- **Group size**: Number of images per GIF. Default is to group by common substrings.
- **Duration**: Duration of each frame in milliseconds (default: 1000ms).
- **Recursive**: Option to search subfolders (yes/no).
- **Filename pattern**: Optional pattern to match image filenames.


```bash
python imagetogif.py
```

#### 2. GIF Renamer (`gif_rename_with_model_name.py`)

This script renames GIFs based on corresponding `.pt` or `.safetensors` files, offering several modes for customization.

##### Options:
- **Image folder**: Directory containing GIFs and model files.
- **Minimum substring length**: Minimum length for matching substrings (default: 4).
- **Mode**:
  - **Normal**: Renames GIFs directly.
  - **With Confirmation**: Shows changes before applying them.
  - **Dry Run**: Simulates renaming to show potential changes without modifying files.


```bash
python gif_rename_with_model_name.py
```

#### 3. Wildcard Creator (`wildcard_creator.py`)

Generates a list of `.pt` and `.safetensors` files from a specified directory, useful for organizing model files.

##### Options:
- **Image folder**: Directory to search for model files.
- **Output file name**: Name of the output text file (default: `model_files.txt`).

```bash
python wildcard_creator.py
```

#### Tips for Use

- **Image to GIF Creator**:
 kren  - The recursive option is beneficial for processing multiple subdirectories.

- **GIF Renamer**:
  - Start with a dry run to preview potential changes.
  - Adjust the minimum substring length to improve matching accuracy.

- **Wildcard Creator**:
  - Ideal for compiling lists of model files for training scripts.

#### Configurable Parameters

- **Image to GIF Creator (`imagetogif.py`)**:
  - **`output_folder`**: Default folder where GIFs are saved.
  - **`group_size`**: Number of images per GIF. Default is set to group by common substrings.
  - **`duration`**: Duration of each frame in milliseconds.
  - **`recursive`**: Boolean option to search subdirectories.
  - **`filename_pattern`**: Pattern to filter image filenames.

- **GIF Renamer (`gif_rename_with_model_name.py`)**:
  - **`min_substring_length`**: Minimum length for matching substrings (default: 4).
  - **`mode`**: Choose between Normal, With Confirmation, or Dry Run modes.

- **Wildcard Creator (`wildcard_creator.py`)**:
  - **`output_file_name`**: Name of the text file for saving the list of model files.


#### Common Issues and Solutions

1. **Problem**: Images are not converted into GIFs.
   - **Solution**: 
     - Ensure the image folder path is correct.
     - Verify the presence of image files in the specified directory.
     - Check log files for error messages related to file access or unsupported formats.

2. **Problem**: GIF renaming is incorrect or incomplete.
   - **Solution**: 
     - Use the "Dry Run" mode to preview changes before applying.
     - Adjust the `min_substring_length` parameter to refine matching.

3. **Problem**: Wildcard list creation fails.
   - **Solution**: 
     - Confirm the directory contains `.pt` or `.safetensors` files.
     - Ensure you have write permissions in the output directory.

4. **Problem**: Permission errors when writing files.
   - **Solution**: 
     - Check the permissions of the directories you are writing to.

5. **Problem**: Script crashes with an unknown error.
   - **Solution**: 
     - Consult the log files located in the script directory for detailed error information.
     - Make sure all dependencies are correctly installed using `pip list`.
