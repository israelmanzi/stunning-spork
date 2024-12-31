import pandas as pd
import logging
import argparse

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger()

COLUMN_MAPPINGS_VARIATIONS = {
    'id': ['id', 'user_id', 'userid'],
    'firstName': ['firstname', 'first_name', 'first name'],
    'lastName': ['lastname', 'last_name', 'last name'],
    'phoneNumber': ['phonenumber', 'phone_number', 'phone number', 'contact_number'],
    'countryCode': ['countrycode', 'country_code', 'country code', 'country'],
    'displayName': ['displayname', 'display_name', 'display name', 'name']
}

def normalize_columns(columns):
    normalized_columns = {}
    for col in columns:
        normalized_col = None
        for key, variations in COLUMN_MAPPINGS_VARIATIONS.items():
            if col.strip().lower() in [v.lower() for v in variations]:
                normalized_col = key
                break
        if normalized_col:
            normalized_columns[col] = normalized_col
        else:
            logger.warning(f"Unrecognized column: {col}")
    return normalized_columns

def load_and_extract(file_path, required_columns):
    if file_path.endswith('.xls') or file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path, dtype=str)
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path, dtype=str)
    else:
        raise ValueError("Unsupported file type. Use CSV or Excel.")

    column_map = normalize_columns(df.columns)
    df.rename(columns=column_map, inplace=True)

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing columns in input file: {', '.join(missing_columns)}")
        raise ValueError(f"Missing columns: {', '.join(missing_columns)}")

    for col in required_columns:
        if col not in df:
            df[col] = None

    extracted_df = df[required_columns]
    return extracted_df

def main():
    parser = argparse.ArgumentParser(description="Extract specified columns from a CSV or Excel file.")
    parser.add_argument("file_path", type=str, help="Path to the input file (CSV or Excel)")
    parser.add_argument(
        "--columns",
        type=str,
        nargs="+",
        default=['id', 'firstName', 'lastName', 'phoneNumber', 'countryCode', 'displayName'],
        help="List of required columns to extract",
    )
    args = parser.parse_args()

    try:
        processed_df = load_and_extract(args.file_path, args.columns)
        print("Processed Data:")
        print(processed_df)
    except Exception as e:
        logger.error(f"Error processing file: {e}")

if __name__ == "__main__":
    main()
