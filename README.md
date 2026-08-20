# LiDAR Processor

A lightweight Windows desktop application for batch converting LiDAR `.laz` files to `.las` files.

LiDAR Processor was built to streamline a simple but repetitive GIS workflow: converting downloaded LAZ point-cloud files into LAS files that can be imported and processed in ArcGIS Pro.

## Features

- Batch convert LAZ files to LAS
- Process an entire folder of LiDAR files
- Optionally search subfolders recursively
- Preserve the original folder structure
- Skip files that have already been converted
- Live progress and processing statistics
- Background processing to keep the interface responsive
- Safe cancellation between files
- Processing log
- Export detailed TXT processing reports

## Workflow

```text
LAZ Files
    │
    ▼
LiDAR Processor
    │
    ├── Discover files
    ├── Convert LAZ → LAS
    ├── Track successes, skips, and failures
    └── Generate processing report
    │
    ▼
LAS Files
    │
    ▼
ArcGIS Pro
```

## Screenshot

![LiDAR Processor Interface](images/lidar-processor-interface.png)

## Usage

1. Launch **LiDAR Processor**
2. Select the folder containing your `.laz` files
3. Select an output folder
4. Choose your processing options:
   - Search subfolders
   - Preserve folder structure
   - Skip existing LAS files
5. Start processing
6. Import the resulting LAS files into ArcGIS Pro

## Processing Options

### Search Subfolders

Recursively searches the selected input directory for `.laz` files.

### Preserve Folder Structure

Recreates the input directory structure inside the output directory.

Example:

```text
Input/
├── Maryland/
│   └── tile.laz
└── Virginia/
    └── tile.laz
```

Becomes:

```text
Output/
├── Maryland/
│   └── tile.las
└── Virginia/
    └── tile.las
```

### Skip Existing LAS Files

Prevents files from being processed again if the corresponding `.las` file already exists in the output directory.

## Project Structure

```text
lidar-processor/
│
├── app/
│   ├── __init__.py
│   ├── gui.py
│   ├── processor.py
│   └── utils.py
│
├── tools/
│   └── laszip64.exe
│
├── main.py
├── run_gui.py
├── requirements.txt
└── README.md
```

## Running From Source

### Requirements

- Windows
- Python 3.12+
- LASzip/LAStools `laszip64.exe`

Place `laszip64.exe` inside:

```text
tools/
```

Then run:

```powershell
python run_gui.py
```

## Building the Executable

The application can be packaged as a standalone Windows executable using PyInstaller.

Install PyInstaller:

```powershell
pip install pyinstaller
```

Build:

```powershell
pyinstaller --onefile --windowed --name "LiDAR Processor" --add-binary "tools\laszip64.exe;tools" run_gui.py
```

The executable will be created in:

```text
dist/LiDAR Processor.exe
```

## Technologies Used

- Python
- Tkinter
- PyInstaller
- LASzip / LAStools
- Git
- GitHub

## Project Background

This project was created to automate part of a LiDAR workflow used in GIS. Rather than building a full point-cloud processing suite, the application focuses on one specific task: efficiently converting batches of LAZ files into LAS files for downstream processing in ArcGIS Pro.

## Status

**Version 1.0**

The application has been tested successfully converting LAZ files to LAS files for use in ArcGIS Pro.