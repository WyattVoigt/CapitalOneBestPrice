import pandas as pd

# File paths for HEB and Target product lists
file_path_heb = 'C:/Users/wyatt/CapitalOneBestPrice/products_HEB.csv'
file_path_target = 'C:/Users/wyatt/CapitalOneBestPrice/products_Target.csv'

try:
    # Read HEB and Target data
    df_heb = pd.read_csv(file_path_heb, encoding='latin1', on_bad_lines='skip')
    df_target = pd.read_csv(file_path_target, encoding='latin1', on_bad_lines='skip')

    # Check if 'title' and 'price' are in both DataFrames
    for df, store in zip([df_heb, df_target], ['HEB', 'Target']):
        if 'title' not in df.columns or 'price' not in df.columns:
            raise ValueError(f"{store} data does not contain 'title' and/or 'price' columns.")
    print("Both HEB and Target contain 'title' and 'price' columns.")

    # Initialize lists for storing selected items and prices
    selected_items_heb = []
    selected_items_target = []
    total_cost_heb = 0
    total_cost_target = 0

    # Function to display top 10 matches from a DataFrame
    def display_top_matches(df, search_input, store_name):
        matches = df[df['title'].str.contains(search_input, case=False, na=False)].copy()
        matches['title_length'] = matches['title'].apply(len)
        matches_sorted = matches.sort_values(by='title_length').reset_index(drop=True).head(10)
        
        if matches_sorted.empty:
            print(f"No matches found for '{search_input}' in {store_name}.")
            return None
        else:
            print(f"\nTop 10 matches in {store_name}:")
            for idx, row in matches_sorted.iterrows():
                print(f"{idx + 1}: {row['title']} - ${row['price']}")
            selection = input(f"Select a number from 1-{len(matches_sorted)} or 'N' to skip: ")
            if selection.isdigit() and 1 <= int(selection) <= len(matches_sorted):
                choice = matches_sorted.iloc[int(selection) - 1]
                return choice['title'], float(choice['price'])
            else:
                print("Invalid selection. Skipping this item.")
                return None

    # Main loop for selecting items
    while True:
        search_input = input("Enter an item to search (or type 'Q' to finish): ").strip().lower()
        if search_input == 'q':
            break

        # Display and select top 10 items from HEB
        heb_choice = display_top_matches(df_heb, search_input, "HEB")
        if heb_choice:
            title, price = heb_choice
            selected_items_heb.append(title)
            total_cost_heb += price

        # Display and select top 10 items from Target
        target_choice = display_top_matches(df_target, search_input, "Target")
        if target_choice:
            title, price = target_choice
            selected_items_target.append(title)
            total_cost_target += price

    # Determine and output the cheaper list
    if selected_items_heb or selected_items_target:
        print("\nYour Selected Items:")
        if total_cost_heb < total_cost_target:
            print(f"\nCheapest Store: HEB\nTotal Cost: ${total_cost_heb:.2f}")
            print("Items:")
            for item in selected_items_heb:
                print(f" - {item}")
        else:
            print(f"\nCheapest Store: Target\nTotal Cost: ${total_cost_target:.2f}")
            print("Items:")
            for item in selected_items_target:
                print(f" - {item}")
    else:
        print("No items were selected.")

except FileNotFoundError:
    print(f"File not found: {file_path_heb} or {file_path_target}")
except UnicodeDecodeError:
    print("Encoding error. Try a different encoding like 'latin1' or 'ISO-8859-1'.")
except ValueError as ve:
    print(ve)
except Exception as e:
    print(f"An error occurred: {e}")
