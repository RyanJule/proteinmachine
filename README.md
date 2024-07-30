# Protein Scraper

This project is a standalone Web Scraper that extracts protein data from UniProt based on Uniprot IDs with the option to validate scraped data against an existing dataset.

## Requirements

- Windows, Mac, or Linux OS
- Internet connection

## Setup Instructions

1. **Download the Executable**:
   - Download the appropriate executable artifact for your Operating System from the Actions tab

2. **Run the Executable**:
   - Set up an excel sheet with the list of proteins you want to have scraped. 
   - Look at test_proteins.xlsx from the repo for an example of the spreadsheet formatting.
   - Make sure you have uniprot ids listed in a column titled 'Protein ID'

3. **Run the Executable**:
   - Doubleclick on the executable wherever you elected to have it downloaded

## Usage

1. **Input File**: Select the input Excel file containing the protein IDs.
2. **Validate Data**: Check this option if you want to validate the scraped data against the input data.
3. **Run**: Click the 'Run' button to start the scraping process.
4. **Progress**: The progress bar will indicate the status of the scraping process.
5. **Results**: results will be stored in the same directory as the input file with _scraped appended to the filename

## Notes

- Make sure you have a stable internet connection as the scraper fetches data from online sources.
- If there are any issues or discrepancies, they will be logged in a file named `discrepancies.txt`.

## Troubleshooting

- If you encounter any issues, make sure all dependencies are installed correctly by checking the `requirements.txt` file.
- Ensure you have the correct version of Python installed.
- For any further assistance, please raise an issue on the repository.
