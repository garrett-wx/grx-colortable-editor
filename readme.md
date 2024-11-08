# Color Table Creator

**Author**: Garrett Helms

## Overview

Color Table Creator is a graphical user interface (GUI) tool built using Python and Tkinter that allows users to create, edit, and save color tables with a variety of customizable settings. This tool is useful for applications that require a structured approach to color mapping based on data values, particularly in fields such as radar imaging, scientific visualization, or data representation.

## Features

- **File Menu**:
  - **Open Color Table**: Load an existing color table file.
  - **Save Color Table**: Save the current color table configuration to a file.
  - **Exit**: Close the application.

- **Settings**:
  - Configure **Product**, **Units**, **Scale**, **Offset**, and **Step** values for the color table.
  - Define an **RF (Reference Field) Color** with a color picker.

- **Color Entries**:
  - Add individual color entries to the color table with custom value ranges.
  - Select color types (single, solid, gradient) and color formats (RGB, RGBA).
  - **Screen Color Picker**: Select colors directly from the screen.
  - Auto-sorting of color entries based on value.

- **Preview Mode**:
  - A preview window shows the color gradient of the entire table, with tick marks and labels.
  - Displays the RF Color as a reference in the preview area.

- **File Format Compatibility**:
  - Supports opening and saving color tables in various formats, including **ColorTable** blocks and **Legacy Formats** (SolidColor, SolidColor4, Color, Color4).
  - Capable of handling comments, empty lines, and multi-line definitions in color table files.

## Installation

### Download the Executable (Recommended)

You can download the latest version of Color Table Creator as an executable file from the [Releases](https://github.com/your-repo/releases) section of the repository. After downloading, extract the ZIP file and run the `.exe` file to start the program.

### Run from Source (Alternative)

If you prefer to run the program from source:

1. Download the source code and save it as `color_table_creator.py`.
2. Install the required Python libraries:
    ```bash
    pip install pillow pyautogui pynput
    ```
3. Run the program using:
    ```bash
    python color_table_creator.py
    ```

## Usage

1. **Open the Program**: Launch the `Color Table Creator` and select settings for Product, Units, Scale, Offset, and Step.
2. **Add Colors**:
   - Click on **Add Color** to insert a new color entry.
   - Choose a color type (single, solid, gradient) and format (RGB or RGBA).
   - Use **Pick Screen Color** to capture a color from anywhere on your screen.
3. **Preview the Color Table**: Click **Preview Color Table** to visualize the colors and settings before saving.
4. **Save the Table**: Save your configuration as a text file by selecting **Save Color Table** from the File menu.

## File Format Details

### Supported Color Formats

- **ColorTable Block**: Supports modern `ColorTable { ... }` format with keys such as `Category`, `Units`, `Scale`, `Offset`, `Step`, and `RF`.
- **Legacy Formats**:
  - **SolidColor**: `SolidColor: value R G B`
  - **SolidColor4**: `SolidColor4: value R G B A`
  - **Color**: `Color: value R G B R G B`
  - **Color4**: `Color4: value R G B A R G B A`
  - **RF**: Specifies the reference field color as `RF: R G B`

### Example Color Table File

```plaintext
Product: Reflectivity
Units: dBZ
Scale: 1
Offset: 0
Step: 5

SolidColor: 10 255 0 0
SolidColor4: 20 0 255 0 128
Color: 30 0 0 255 255 255 0
Color4: 40 255 255 0 128 0 0 255 128

RF: 255 255 255


## License
This software is open-source and free to use for educational or non-commercial purposes. Contact Garrett Helms for additional licensing information.
