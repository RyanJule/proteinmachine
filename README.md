# Protein Scraper

This project is a Protein Scraper that extracts protein data from UniProt and validates it against an existing dataset. 

## Requirements

- Windows OS
- Git Bash (for running the shell script)
- Internet connection

## Setup Instructions

1. **Download and Install Git Bash**:
   - If you don't have Git Bash, download and install it from [here](https://gitforwindows.org/).

2. **Clone the Repository**:
   - Open Git Bash and run the following command to clone the repository:
    ```bash
     git clone https://github.com/RyanJule/proteinmachine.git
     cd proteinmachine
     ```
3. **Run the Setup Script**:
   - Make sure you are in the repository directory and run the following command to execute the setup script:
     ```bash
     ./setup.sh
     ```

4. **Run the Application**:
   - After the setup script completes, you can start the application by running:
     ```bash
     source venv/Scripts/activate
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
