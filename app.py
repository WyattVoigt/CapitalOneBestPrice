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

def calculate_savings():
    cost_heb = session.get('total_cost_heb', 0.0)
    cost_target = session.get('total_cost_target', 0.0)
    cost_walmart = session.get('total_cost_walmart', 0.0)

    # Filter out stores with a cost of 0.0
    costs = {"HEB": cost_heb, "Target": cost_target, "Walmart": cost_walmart}
    non_zero_costs = {store: cost for store, cost in costs.items() if cost > 0}

    if len(non_zero_costs) < 2:
        return 0.0, "N/A"

    cheapest_store = min(non_zero_costs, key=non_zero_costs.get)
    cheapest_cost = non_zero_costs[cheapest_store]
    remaining_costs = [cost for store, cost in non_zero_costs.items() if store != cheapest_store]
    average_of_higher = sum(remaining_costs) / len(remaining_costs)
    savings = round(average_of_higher - cheapest_cost, 2)

    return savings, cheapest_store

@app.route("/", methods=["GET", "POST"])
def index():
    initialize_session_data()

    search_input = ""
    top_heb_matches = []
    top_target_matches = []
    top_walmart_matches = []

    if request.method == "POST" and 'search' in request.form:
        search_input = request.form.get("search_input", "").strip().lower()

        matches_heb = df_heb[df_heb['title'].str.contains(search_input, case=False, na=False)].copy()
        matches_heb['title_length'] = matches_heb['title'].str.len()
        top_heb_matches = matches_heb.sort_values(by='title_length').head(10).to_dict('records')

        matches_target = df_target[df_target['title'].str.contains(search_input, case=False, na=False)].copy()
        matches_target['title_length'] = matches_target['title'].str.len()
        top_target_matches = matches_target.sort_values(by='title_length').head(10).to_dict('records')

        matches_walmart = df_walmart[df_walmart['Title'].str.contains(search_input, case=False, na=False)].copy()
        matches_walmart['title_length'] = matches_walmart['Title'].str.len()
        top_walmart_matches = matches_walmart.sort_values(by='title_length').head(10).to_dict('records')

    savings, cheaper_store = calculate_savings()

    return render_template("index.html", search_input=search_input,
                           top_heb_matches=top_heb_matches, top_target_matches=top_target_matches,
                           top_walmart_matches=top_walmart_matches,
                           selected_items_heb=session['selected_items_heb'],
                           selected_items_target=session['selected_items_target'],
                           selected_items_walmart=session['selected_items_walmart'],
                           total_cost_heb=f"{session['total_cost_heb']:.2f}",
                           total_cost_target=f"{session['total_cost_target']:.2f}",
                           total_cost_walmart=f"{session['total_cost_walmart']:.2f}",
                           savings=f"{savings:.2f}",
                           cheaper_store=cheaper_store,
                           enumerate=enumerate)

@app.route("/add_items", methods=["POST"])
def add_items():
    initialize_session_data()

    top_heb_matches = request.json.get('top_heb_matches', [])
    top_target_matches = request.json.get('top_target_matches', [])
    top_walmart_matches = request.json.get('top_walmart_matches', [])
    selected_heb_index = int(request.json.get('selected_heb', -1))
    selected_target_index = int(request.json.get('selected_target', -1))
    selected_walmart_index = int(request.json.get('selected_walmart', -1))

    if selected_heb_index >= 0 and selected_heb_index < len(top_heb_matches):
        selected_heb = top_heb_matches[selected_heb_index]
        price = round(float(selected_heb['price']), 2)
        session['selected_items_heb'].append((selected_heb['title'], price))
        session['total_cost_heb'] = round(session['total_cost_heb'] + price, 2)

    if selected_target_index >= 0 and selected_target_index < len(top_target_matches):
        selected_target = top_target_matches[selected_target_index]
        price = round(float(selected_target['price']), 2)
        session['selected_items_target'].append((selected_target['title'], price))
        session['total_cost_target'] = round(session['total_cost_target'] + price, 2)

    if selected_walmart_index >= 0 and selected_walmart_index < len(top_walmart_matches):
        selected_walmart = top_walmart_matches[selected_walmart_index]
        price = round(float(selected_walmart['PRICE_CURRENT']), 2)
        session['selected_items_walmart'].append((selected_walmart['Title'], price))
        session['total_cost_walmart'] = round(session['total_cost_walmart'] + price, 2)

    session.modified = True
    savings, cheaper_store = calculate_savings()

    return jsonify({
        'selected_items_heb': session['selected_items_heb'],
        'selected_items_target': session['selected_items_target'],
        'selected_items_walmart': session['selected_items_walmart'],
        'total_cost_heb': f"{session['total_cost_heb']:.2f}",
        'total_cost_target': f"{session['total_cost_target']:.2f}",
        'total_cost_walmart': f"{session['total_cost_walmart']:.2f}",
        'savings': f"{savings:.2f}",
        'cheaper_store': cheaper_store
    })

@app.route("/clear_items", methods=["POST"])
def clear_items():
    session['selected_items_heb'] = []
    session['selected_items_target'] = []
    session['selected_items_walmart'] = []
    session['total_cost_heb'] = 0.0
    session['total_cost_target'] = 0.0
    session['total_cost_walmart'] = 0.0
    session.modified = True
    return jsonify(success=True)

@app.route("/nextpage", methods=["GET"])
def nextpage():
    total_costs = {
        "HEB": session.get('total_cost_heb', 0.0),
        "Target": session.get('total_cost_target', 0.0),
        "Walmart": session.get('total_cost_walmart', 0.0)
    }
    non_empty_stores = {store: cost for store, cost in total_costs.items() if cost > 0.0}

    if non_empty_stores:
        cheapest_store = min(non_empty_stores, key=non_empty_stores.get)
        running_total = non_empty_stores[cheapest_store]
    else:
        cheapest_store = "N/A"
        running_total = 0.0

    all_items = {
        "HEB": session.get('selected_items_heb', []),
        "Target": session.get('selected_items_target', []),
        "Walmart": session.get('selected_items_walmart', [])
    }
    items_for_cheapest_store = all_items.get(cheapest_store, [])

    return render_template(
        "nextpage.html",
        cheapest_store=cheapest_store,
        running_total=f"{running_total:.2f}",
        items_for_cheapest_store=items_for_cheapest_store
    )

if __name__ == "__main__":
    app.run(debug=True)

