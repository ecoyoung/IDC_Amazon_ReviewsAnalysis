**English** | [简体中文](README.md)

# Amazon Review Analysis Tool
This is an application for analyzing Amazon product reviews.
Development team: Haiyi IDC
Data source: reviews bulk-exported via Shulex
Format: .XLSX

## Features

- Data preprocessing:
  - Supports Excel file upload
  - Keeps key columns: Asin, Title, Content, Model, Rating, Date
  - Automatically adds an ID column for review sorting
  - Exports the processed data as a new Excel file

## Installation
1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Start the application
2. Click "Browse files" to upload an Excel file
3. Click "Data Processing" to process the data and display the results. The Asin, Title, Content, Model, Rating, Rating, Date columns are retained, and reviews are classified by Rating into a column named Review Type: a Rating of 4 or 5 is positive, 3 is neutral, and 2 or 1 is negtive. A new ID column is added as the first column to locate reviews
4. Click the "Download processed data" button to export the processed file; TXT and EXCEL formats are supported. In addition to downloading all reviews, you can also download only positive or negtive reviews

## Input File Requirements
The Excel file contains the following columns:
- Asin
- Title
- Content
- Model
- Rating
- Date
