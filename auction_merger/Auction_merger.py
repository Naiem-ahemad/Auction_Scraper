import os
import pandas as pd
from datetime import datetime, timedelta

def normalize_column(col_name):
    return col_name.strip().lower().replace(":", "").replace("#", "").replace("  ", " ").strip()

def main():
    yesterday = datetime.now() - timedelta(days=1)
    auction_date = yesterday.strftime("%m/%d/%Y")
    folder_name = auction_date.replace("/", "-")

    if not os.path.exists(folder_name):
        print(f"[✗] Folder '{folder_name}' not found!")
        return

    # Target column names in final output
    desired_columns = [
        "County",
        "Auction Sold",
        "Case #",
        "Parcel ID",
        "Property Address",
        "Final Judgment Amount",
        "Amount",
        "Sold To"
    ]

    # Normalized key map for fuzzy matching
    expected_map = {
        "county": "County",
        "auction sold": "Auction Sold",
        "case": "Case #",
        "case number": "Case #",
        "parcel id": "Parcel ID",
        "property address": "Property Address",
        "final judgment amount": "Final Judgment Amount",
        "amount": "Amount",
        "sold to": "Sold To",
    }

    all_data = []

    print(f"[+] Reading Excel files from: '{folder_name}'")

    for file in os.listdir(folder_name):
        if file.endswith(".xlsx"):
            file_path = os.path.join(folder_name, file)
            try:
                df = pd.read_excel(file_path)

                # Build normalized column mapping
                normalized_map = {
                    normalize_column(col): col
                    for col in df.columns
                }

                # Remap columns to standard names
                col_mapping = {}
                for norm_col, orig_col in normalized_map.items():
                    if norm_col in expected_map:
                        col_mapping[orig_col] = expected_map[norm_col]

                df = df.rename(columns=col_mapping)

                # Skip if "Sold To" column doesn't exist
                if "Sold To" not in df.columns:
                    print(f"[!] Skipping '{file}' — 'Sold To' column not found")
                    continue

                filtered_df = df[df["Sold To"].astype(str).str.strip().str.lower() == "3rd party bidder"]

                if filtered_df.empty:
                    print(f"[-] No '3rd Party Bidder' found in: {file}")
                    continue

                # Add 'County' from file name
                county_name = file.split("_")[0].capitalize()
                filtered_df.insert(0, "County", county_name)

                # Ensure all desired columns exist
                for col in desired_columns:
                    if col not in filtered_df.columns:
                        filtered_df[col] = ""

                # Reorder columns
                filtered_df = filtered_df[desired_columns]

                all_data.append(filtered_df)
                print(f"[✓] Added {len(filtered_df)} rows from '{file}'")

            except Exception as e:
                print(f"[✗] Error reading '{file}': {e}")

    if not all_data:
        print("[-] No data to merge.")
        return

    print("[+] Merging data...")

    final_df = pd.concat(all_data, ignore_index=True)
    output_file = f"merged_{folder_name}.xlsx"
    final_df.to_excel(output_file, index=False)
    print(f"[✓] Merged file created: '{output_file}'")

if __name__ == "__main__":
    main()
