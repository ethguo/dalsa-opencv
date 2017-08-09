# Anaconda + OpenCV Environment Setup Guide

## Step 1. Install Anaconda

 - Download the lastest version Windows installer for Anaconda3 (Python 3.6 version) from:

	[https://www.continuum.io/downloads#windows](https://www.continuum.io/downloads#windows)

 - Run the installer (`Anaconda3-4.X.X-Windows-x86_64.exe`).
 - Agree to the License Agreement.
 - Select "Install for Just Me".
 - Select both checkbox options "Add Anaconda to my PATH environment variable" and "Register Anaconda as my default Python 3.6". 
 - Verify that the installer completes successfully.

## Step 2. Setup the conda environment

 - Navigate to this folder (`...\opencv`) in Windows Explorer.
 - Double-click `setup.bat`.
 - Verify that setup script completes successfully.

## Using the environment

To run Python scripts in the environment from a command prompt, you must first enter the environment using the following command:

```
> activate opencv
```

To use the environment from an IDE or other program, point your IDE of choice to 

```
C:\Users\[YOUR USERNAME]\AppData\Local\Continuum\Anaconda3\envs\opencv\python.exe
```

(Note: your installation location might be different.)