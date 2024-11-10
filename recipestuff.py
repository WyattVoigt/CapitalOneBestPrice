from flask import Flask, render_template, request, jsonify, session
import pandas as pd

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Load data from CSV files
file_path_heb = 'C:/Users/wyatt/CapitalOneBestPrice/products_HEB.csv'
file_path_target = 'C:/Users/wyatt/CapitalOneBestPrice/products_Target.csv'
file_path_walmart = r'C:/Users/wyatt/CapitalOneBestPrice/products_Walmart(kaggle).csv'

df_heb = pd.read_csv(file_path_heb, encoding='latin1', on_bad_lines='skip')
df_target = pd.read_csv(file_path_target, encoding='latin1', on_bad_lines='skip')
df_walmart = pd.read_csv(file_path_walmart, encoding='latin1', on_bad_lines='skip')

# Clear session data on app start
@app.before_first_request
def clear_session():
    session.clear()

# Helper function to initialize session data
def initialize_session_data():
    if 'selected_items_heb' not in session:
        session['selected_items_heb'] = []
    if 'selected_items_target' not in session:
        session['selected_items_target'] = []
    if 'selected_items_walmart' not in session:
        session['selected_items_walmart'] = []
    if 'total_cost_heb' not in session:
        session['total_cost_heb'] = 0.0
    if 'total_cost_target' not in session:
        session['total_cost_target'] = 0.0
    if 'total_cost_walmart' not in session:
        session['total_cost_walmart'] = 0.0

def get_item_price(item, store_df, store_column, price_column):
    matches = store_df[store_df[store_column].str.contains(item, case=False, na=False)]
    if not matches.empty:
        return matches[price_column].min()  # Get the lowest price for the item
    return None  # Return None if the item isn't found

def calculate_recipe_cost(recipe):
    # Dictionary to store total costs for each store
    store_costs = {'HEB': 0, 'Target': 0, 'Walmart': 0}

    # Loop through each item in the recipe
    for item in recipe:
        # Get price from each store if available
        price_heb = get_item_price(item, df_heb, 'title', 'price')
        price_target = get_item_price(item, df_target, 'title', 'price')
        price_walmart = get_item_price(item, df_walmart, 'Title', 'PRICE_CURRENT')

        # Add prices to respective store costs if price is found
        if price_heb is not None:
            store_costs['HEB'] += price_heb
        if price_target is not None:
            store_costs['Target'] += price_target
        if price_walmart is not None:
            store_costs['Walmart'] += price_walmart

    # Find the store with the lowest total cost
    cheapest_store = min(store_costs, key=store_costs.get)
    return cheapest_store, store_costs[cheapest_store]

@app.route("/calculate_recipe_cost", methods=["POST"])
def calculate_recipe():
    recipe = request.json.get('recipe', [])
    if not recipe:
        return jsonify({"error": "Recipe list is empty"}), 400

    cheapest_store, total_cost = calculate_recipe_cost(recipe)

    return jsonify({
        "cheapest_store": cheapest_store,
        "total_cost": f"{total_cost:.2f}"
    })

# Existing routes (index, add_items, clear_items) would remain the same

if __name__ == "__main__":
    app.run(debug=True)
