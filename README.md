# Character Information Scraper

## Description

This scraper is designed to gather information about specified characters, primarily from Wikipedia. It extracts textual data from their Wikipedia pages and downloads related images using Google Images.

## Setup and Installation

Follow these steps to set up your environment and install the necessary dependencies.

### 1. Clone the Repository (Optional)

If you haven't already, clone the repository to your local machine:
```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Create a Virtual Environment (Recommended)

It's highly recommended to use a virtual environment to manage project dependencies.

*   On macOS and Linux:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
*   On Windows:
    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```
You should see `(.venv)` at the beginning of your command prompt.

### 3. Install Dependencies

Install all required packages using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 4. WebDriver for Selenium

This scraper uses Selenium to automate web browser interaction, which requires a WebDriver.

*   **What is a WebDriver?** A WebDriver is an executable that acts as a bridge between your script (Selenium) and the web browser (e.g., Chrome, Firefox). You need a WebDriver that matches your browser type and version.
*   **Installation**:
    1.  Identify your browser (e.g., Google Chrome) and its version.
    2.  Download the corresponding WebDriver. For example, ChromeDriver for Chrome or GeckoDriver for Firefox.
    3.  For detailed instructions and download links, please refer to the official Selenium documentation: [Selenium WebDriver Installation](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/)
*   **Configuration**:
    The WebDriver executable must be placed in a directory that is part of your system's **PATH environment variable**. Alternatively, you can specify the path to the WebDriver executable in the script, but the current version of this scraper expects it to be in the PATH.

    If the WebDriver is not correctly installed and accessible via the PATH, Selenium will not be able to launch the browser, and the scraper will fail.

## Running the Scraper

Once setup is complete, you can run the scraper using `main.py`.

### Command-Line Arguments

The script accepts the following command-line arguments:

*   `-d <path_to_txt_file>`: Specify the path to a text file containing a list of character names (one name per line).
*   `-t <number_of_threads>`: Specify the number of threads to use. (Note: While this argument is defined, its functionality related to threading in data gathering might not be fully implemented in the current version.)

### Examples

*   **Scraping a list of characters from a file:**
    ```bash
    python main.py -d characters.txt
    ```
    (Assuming `characters.txt` exists and contains names like "Albert Einstein", "Marie Curie", etc.)

*   **Scraping a single character (interactive prompt):**
    If you run the script without any arguments, it will prompt you to enter a single character name:
    ```bash
    python main.py
    ```
    It will then ask: `Write the name of the character you want to search: `

### Output

*   **Text Data**: Extracted textual information from Wikipedia pages is saved in `.txt` files within the `data/<CharacterName>/` directory.
*   **Images**: Downloaded images are saved in the `img/<CharacterName>/` directory.

## Running Tests

Unit tests are provided to ensure the functionality of different components of the scraper.

To run the tests:

1.  Make sure you have installed `pytest` and `pytest-mock` (they are included in `requirements.txt`).
2.  Navigate to the root directory of the project.
3.  Run the following command:
    ```bash
    pytest
    ```
This command will automatically discover and run all tests located in the `tests/` directory.
