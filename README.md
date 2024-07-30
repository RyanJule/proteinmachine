# Protein Scraper

This project is a Protein Scraper that extracts protein data from UniProt and validates it against an existing dataset.

## Requirements

- Windows OS
- Internet connection

## Setup Instructions

1. **Download the Repository**:
   - Download the repository as a ZIP file from [here](https://github.com/RyanJule/proteinmachine/archive/refs/heads/main.zip) and extract it.

2. **Run the Setup Script**:
   - Navigate to the extracted folder and double-click on `setup.bat` to run the setup script.

3. **Run the Application**:
   - After the setup script completes, activate the virtual environment by running:
     ```batch
     venv\Scripts\activate
     ```
   - Start the application by running:
     ```batch
     python proteinscraper.py
     ```

## Usage

1. **Input File**: Select the input Excel file containing the protein IDs.
2. **Output File**: Select the output path where the scraped data will be saved.
3. **Validate Data**: Check this option if you want to validate the scraped data against the input data.
4. **Run**: Click the 'Run' button to start the scraping process.
5. **Progress**: The progress bar will indicate the status of the scraping process.

## Notes

- Make sure you have a stable internet connection as the scraper fetches data from online sources.
- If there are any issues or discrepancies, they will be logged in a file named `discrepancies.txt`.

## Troubleshooting

- If you encounter any issues, make sure all dependencies are installed correctly by checking the `requirements.txt` file.
- Ensure you have the correct version of Python installed.
- For any further assistance, please raise an issue on the repository.
