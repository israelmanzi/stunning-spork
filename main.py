import pandas as pd
import logging
import re
import argparse

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger()

COLUMN_VARIATIONS = {
    'firstName': ['firstname', 'first name', 'first_name'],
    'lastName': ['lastname', 'last name', 'last_name'],
    'phoneNumber': ['phonenumber', 'phone', 'contact', 'phone number', 'phone_number', 'contact_number'],
    'countryCode': ['countrycode', 'country code', 'country_code', 'country'],
    'displayName': ['displayname', 'display name', 'display_name', 'name'],
    'id': ['id', 'user_id', 'user id', 'userid'],
}

def validate_phone_number(phone_number):
    if not isinstance(phone_number, str):
        return False
    return bool(re.match(r'^\d{7,11}$', phone_number))

def validate_country_code(country_code):
    if not isinstance(country_code, str):
        return False
    return bool(re.match(r'^\d{1,3}$', country_code))

def normalize_column_name(col_name):
    for field, variations in COLUMN_VARIATIONS.items():
        if col_name.strip().lower() in [v.lower() for v in variations]:
            return field
    return None

def load_and_process_file(file_path):
    if file_path.endswith('.xls') or file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path, dtype=str)
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path, dtype={col: str for col in COLUMN_VARIATIONS.keys()})
    else:
        raise ValueError('Unsupported file type')

    normalized_columns = {}
    for col in df.columns:
        normalized_name = normalize_column_name(col)
        if normalized_name:
            normalized_columns[normalized_name] = df[col]
        else:
            logger.warning(f"Skipping column: '{col}' as it does not match any expected names.")

    processed_data = []
    for _, row in df.iterrows():
        if row.get('name') is not None:
            first_name, last_name = parse_full_name(row.get('name'))
        else:
            first_name = row.get('firstName', '')
            last_name = row.get('lastName', '')

        phone_number = row.get('phoneNumber', '')
        country_code = normalize_country_code(row.get('countryCode', ''))
        display_name = row.get('displayName', f"{first_name} {last_name}")
        id = row.get('id', '')

        if not validate_phone_number(phone_number):
            logger.warning(f"Invalid phone number: {phone_number}")
            continue

        if not validate_country_code(country_code):
            logger.warning(f"Invalid country code: {country_code}")
            continue

        processed_data.append({
            'id': id,
            'firstName': first_name,
            'lastName': last_name,
            'displayName': display_name,
            'phoneNumber': phone_number,
            'countryCode': country_code,
        })

    processed_df = pd.DataFrame(processed_data)

    # print("Processed DataFrame:")
    # print(processed_df)

    missing_columns = [col for col in ['firstName', 'lastName', 'phoneNumber', 'countryCode'] if col not in processed_df.columns]
    if missing_columns:
        logger.error(f"Missing required columns after parsing: {', '.join(missing_columns)}")
        raise ValueError(f"Missing required columns after parsing: {', '.join(missing_columns)}")

    return processed_df[['id', 'firstName', 'lastName', 'displayName', 'phoneNumber', 'countryCode']]

def parse_full_name(name):
    parts = name.strip().split()
    if len(parts) == 1:
        return parts[0], ''
    return parts[0], ' '.join(parts)

def normalize_country_code(country_code):
    return country_code.strip()

def main():
    parser = argparse.ArgumentParser(description="Process a CSV or Excel file and normalize columns.")
    parser.add_argument('file_path', type=str, help='Path to the input file (CSV or Excel)')
    
    args = parser.parse_args()
    try:
        processed_df = load_and_process_file(args.file_path)
        print("Processed DataFrame:")
        print(processed_df)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
