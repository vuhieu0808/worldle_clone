# Worldle Clone

This project is a clone of the popular geography guessing game, Worldle. It uses Python and SVG images to create an interactive experience where users can guess countries based on their shape.

## Project Structure

```
.
├── src
│   ├── assets
│   │   ├── countries
│   │   └── country.json
│   ├── compute.py
│   └── main.py
├── requirements.txt
└── README.md
```

- `src/assets/`: Contains static files, such as SVG data for countries.
  - `countries/`: Holds individual SVG files for each country.
  - `country.json`: A JSON file with a list of countries.
- `src/`: Contains the main source code for the application.
  - `compute.py`: Handles game logic and computations.
  - `main.py`: The main entry point for the application.
- `requirements.txt`: A list of Python dependencies required for the project.
- `README.md`: This file.

## Setup and Installation

### 1. Environment Setup

It is recommended to use a virtual environment to manage project dependencies.

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

### 2. Install Dependencies

Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

### 3. Download Assets

The assets for this project are not included in the repository. You will need to download them from the following link and extract them into the `src/assets/` directory.

**[Download Assets](https://drive.google.com/drive/folders/1T36PP8BZZI501U67Jd0buTQlu9ZLOSGW?usp=sharing)**

After downloading and extracting, your `src/assets/` directory should look like this:

```
src/assets/
├── countries/
│   ├── AD.svg
│   ├── AE.svg
│   └── ...
└── country.json
```

## How to Run

Once you have completed the setup, you can run the main application from the `src/` directory:

```bash
python src/main.py
```
