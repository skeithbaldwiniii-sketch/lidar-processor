# LiDAR Processor

A Windows desktop application for batch processing LiDAR LAZ files.

The current version provides a graphical interface for converting LAZ files to LAS using LASzip/LAStools.

## Current Features

- Convert LAZ files to LAS
- Batch process multiple files
- Recursively search subfolders
- Preserve the input folder structure
- Optionally skip existing LAS files
- Background processing keeps the GUI responsive
- Live processing progress
- Converted, skipped, and failed file counts
- Safe cancellation between files
- Processing log
- Save detailed processing reports as TXT files

## Current Workflow

```text
LAZ files
   |
   v
Input Folder
   |
   v
Recursive File Discovery
   |
   v
LAZ → LAS Conversion
   |
   +----> Converted
   |
   +----> Skipped
   |
   +----> Failed
   |
   v
Output Folder
   |
   v
Processing Report

