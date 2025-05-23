import os
import pandas as pd
from datetime import datetime, timedelta

def normalize_column(col_name):
    return col_name.strip().lower().replace(":", "")

def main():
    yesterday = datetime.now() - timedelta(days=1)
    auction_date = yesterday.strftime("%m/%d/%Y")
    folder_name = auction_date.replace("/", "-")

    if not os.path.exists(folder_name):
        print(f"[✗] Folder '{folder_name}' not found!")
        return

    all_data = []
    all_columns = set()

    print(f"[+] Reading Excel files from: '{folder_name}'")

    for file in os.listdir(folder_name):
        if file.endswith(".xlsx"):
            file_path = os.path.join(folder_name, file)
            try:
                df = pd.read_excel(file_path)

                # Normalize column names for consistent access
                normalized_map = {normalize_column(col): col for col in df.columns}

                sold_to_col = None
                for norm, orig in normalized_map.items():
                    if norm == "sold to":
                        sold_to_col = orig
                        break

                if not sold_to_col:
                    print(f"[!] Skipping '{file}' — 'Sold To' column not found")
                    continue

                filtered_df = df[df[sold_to_col].astype(str).str.strip().str.lower() == "3rd party bidder"]

                if filtered_df.empty:
                    print(f"[-] No '3rd Party Bidder' found in: {file}")
                    continue

                # Add 'County' column from file name
                county_name = file.split("_")[0].capitalize()
                filtered_df.insert(0, "County", county_name)

                all_columns.update(filtered_df.columns)
                all_data.append(filtered_df)

                print(f"[✓] Added {len(filtered_df)} rows from '{file}'")

            except Exception as e:
                print(f"[✗] Error reading '{file}': {e}")

    if not all_data:
        print("[-] No data to merge.")
        return

    print("[+] Merging data...")

    # Ensure 'County' is first column in final DataFrame
    all_columns = sorted(list(all_columns))
    if "County" in all_columns:
        all_columns.remove("County")
    final_columns_order = ["County"] + all_columns

    for i in range(len(all_data)):
        all_data[i] = all_data[i].reindex(columns=final_columns_order)

    final_df = pd.concat(all_data, ignore_index=True)
    output_file = f"merged_{folder_name}.xlsx"
    final_df.to_excel(output_file, index=False)
    print(f"[✓] Merged file created: '{output_file}'")

if __name__ == "__main__":
    main()
