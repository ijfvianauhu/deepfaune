# <img src="img/wildIntel_logo.webp" alt="Wildintel DeepFaune Runner" height="60">  Wildintel DeepFaune Runner

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![License](https://img.shields.io/badge/license-GPLv3-blue.svg)
[![WildINTEL](https://img.shields.io/badge/WildINTEL-v1.0-blue)](https://wildintel.eu/)

<hr>

## Utilities for running DeepFaune detection in Docker

## 🚀 Features

- **Single Image Detection**: Use the `testDetector.py` script with the `CustomDetector` class to process a folder of images.  
  Generates a single CSV file with all detections, including animal crops, human and vehicle boxes.

- **Batch Multi-Model Detection**: Use the `run_all_detectors.py` script with the `CustomDetector2` class to run multiple YOLO models with different thresholds.  
  Generates one CSV file per model-threshold combination, including detailed metadata (`detector`, `threshold`, `xmin`, `ymin`, `xmax`, `ymax`, `animal_count`, `num_humans`).

- **Docker-based execution**: All DeepFaune workflows can be run via the `setup.sh` script, which handles:  
  - Cloning the DeepFaune repository  
  - Building CPU or GPU Docker images  
  - Running containers with GUI support  
  - Opening interactive shells for debugging  
  - Cleaning up Docker images and volumes

---

## 📋 Requirements

* Python 3.12 or higher  
* Docker and Docker Compose (for containerized execution)  
* NVIDIA GPU + NVIDIA Container Toolkit (optional, for GPU acceleration)  
* DeepFaune model weights (automatically downloaded via the scripts)  
* Access to input image folder

---

## 🧭 Overview

This repository provides an easy-to-use workflow for automatic wildlife detection using DeepFaune YOLO models.  
Users can either run single-image detection for smaller datasets or execute multi-model batch detection with different thresholds.  

All operations are containerized for reproducibility and ease of deployment.  
The `.env` configuration file allows adjusting model versions, CUDA usage, and other runtime settings.

---

# 📦 Installation

Clone the repository:

```bash
git clone https://github.com/ijfvianauhu/deepfaune.git
cd deepfaune
mkdir data
```

# ⚙️ Configuration

Before running the container, you must create your environment configuration file.

Copy the example file:
```bash
cp env.example .env
```
Then, edit the `.env` file to set your configuration parameters.

## Environment Variables

- `VERSION`: Specifies which DeepFaune Docker image version will be used.  Example: `VERSION=v1.4.1`.
- `CUDA`: Controls GPU usage. Example: `CUDA=0`.
- `REPO`: Repository source 
- `USERID`, `GROUPID`: User and group permissions : Set these to match your host system's user and group IDs to avoid 
permission issues when accessing files from the container. Example: `USERID=1000`, `GROUPID=1000`. By default, it uses 
the current user's IDs.

# ▶️ Quick Start

All Docker operations are managed through the `setup.sh` script.

This script handles:

- Cloning the DeepFaune source code (if not already present)
- Building the Docker image (CPU or GPU)
- Running the container (with graphical interface support)
- Opening an interactive shell inside the container
- Destroying the Docker stack

---

## 1️⃣ Build the Docker Image

To build the DeepFaune Docker image:

```bash
./setup.sh build
```

If you want to force a rebuild without using Docker cache:

```bash
./setup.sh build --no-cache
```

What this does:

* Clones the DeepFaune repository at the specified `VERSION` (if not already cloned)
* Selects CPU or GPU profile based on the `CUDA` variable
* Builds the corresponding Docker Compose service:
  * deepfaune-cpu
  * deepfaune-gpuç

## 2️⃣ Run the Container (Graphical Interface Enabled)

To start DeepFaune:

```bash
./setup.sh run
```

This command:

* Selects CPU or GPU profile automatically
* Enables X11 forwarding (xhost +local:docker)
* Launches the appropriate Docker Compose service
* Builds the image if needed

This mode is intended for running DeepFaune with graphical interface support.

## 3️⃣ Open an Interactive Shell

To open a Bash shell inside the container:

```bash
./setup.sh shell
```
This is useful for:

* Debugging
* Manual testing
* Running DeepFaune commands interactively
* Inspecting the environment

The container will be removed automatically when you exit the shell.

## 4️⃣ Destroy the Stack

To stop containers and remove related resources:

```
./setup.sh destroy
```
This will:

* Stop running containers
* Remove local images created by Docker Compose
* Remove associated volumes

Use this if you want a clean reset of the environment.

## Command Summary

| Command              | Description                           |
| -------------------- | ------------------------------------- |
| `./setup.sh build`   | Build Docker image                    |
| `./setup.sh run`     | Run DeepFaune container (GUI enabled) |
| `./setup.sh shell`   | Open interactive shell                |
| `./setup.sh destroy` | Stop and remove containers/images     |

The script automatically reads configuration from the `.env` file and selects:

* The DeepFaune version (VERSION)
* CPU or GPU mode (CUDA)
* Repository source (REPO)
* User and group permissions (USERID, GROUPID)

# 🖥️ Included Applications

This repository includes **two main Python applications** for running DeepFaune detection:

---

## 1️⃣ Single Image Detector

Script  `testDetector.py` contains yhe Detector class `CustomDetector` which purpose is to process a folder of images 
and generate a single CSV file containing all detections. We can use it executing the following command:

```bash
python testDetector.py <IMAGE_FOLDER> <OUTPUT_CSV>
```

Features:

* Loads a specified YOLO model.
* Detects animals, humans, and vehicles.
* Crops animal images for further classification.
* Saves results in a CSV with columns: filename, category, xmin, ymin, xmax, ymax, animal_count, num_humans.

## 2️⃣ Batch Multi-Model Detector

Script `run_all_detectors.py` includes the detector class `CustomDetector2`. The purpose of this script is execute  
multiple YOLO models with different thresholds over a folder of images, generating one CSV per model-threshold combination.

Usage:

```
python run_all_detectors.py <IMAGE_FOLDER> <OUTPUT_FOLDER>
```

Features:

* Supports multiple models: DF, MDS, DFMDS, MDR.
* Runs each model with a set of configurable thresholds (e.g., 0.1, 0.25, 0.5, 0.6, 0.75, 0.9).
* Saves separate CSV files for each combination of model and threshold.
* Includes metadata columns: detector, threshold, along with all detection details (xmin, ymin, xmax, ymax, animal_count, num_humans).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the GNU General Public License v3.0 or later - see the [LICENSE](LICENSE) file for details.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.


## 🏛️ Funding

This work is part of the [WildINTEL project](https://wildintel.eu/), funded by the Biodiversa+ Joint Research Call 2022-2023 “Improved
transnational monitoring of biodiversity and ecosystem change for science and society (BiodivMon)”. Biodiversa+ is the 
European co-funded biodiversity partnership supporting excellent research on biodiversity with an impact for policy and
society. Biodiversa+ is part of the European Biodiversity Strategy for 2030 that aims to put Europe’s biodiversity on a
path to recovery by 2030 and is co-funded by the European Commission. 
