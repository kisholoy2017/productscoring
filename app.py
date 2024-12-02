import streamlit as st
import pandas as pd

# Function to validate factor weights
def validate_weights(weights):
    return sum(weights) == 1.0

# Function to validate sub-value input data
def validate_sub_values(sub_values):
    for factor, ranges in sub_values.items():
        for entry in ranges:
            try:
                float(entry["min"])  # Ensure Min is numeric
                float(entry["max"])  # Ensure Max is numeric
                float(entry["score"])  # Ensure Score is numeric
            except ValueError:
                return False, f"Invalid value in factor {factor}. Min, Max, and Score must all be numeric."
    return True, None

# Function to calculate scores
def calculate_scores(data, weights, sub_value_mappings):
    scores = []
    for _, row in data.iterrows():
        score = 0
        for factor, ranges in sub_value_mappings.items():
            value = row[factor]
            for entry in ranges:
                if entry["min"] <= value <= entry["max"]:
                    score += float(weights[factor]) * float(entry["score"])
                    break
        scores.append(score)
    return scores

# Streamlit App
st.title("Product Scoring Application")

# Step 1: Upload CSV File
st.header("Step 1: Upload Product Data")
uploaded_file = st.file_uploader("Upload your CSV file containing product data", type=["csv"])
if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.write("Preview of Uploaded Data:")
    st.dataframe(data.head())

# Step 2: Input Factor Weights
if uploaded_file:
    st.header("Step 2: Input Factor Weights")
    st.write("Provide weights for each factor. The total must equal 1.")

    factors = ["Cost", "Margin", "CAC", "Return Rate", "Stock Status"]
    weights = {}

    for factor in factors:
        weights[factor] = st.number_input(
            f"Weight for {factor}",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            format="%.2f",
            placeholder="e.g., 0.2",
            key=f"weight_{factor}"
        )

    if st.button("Submit Weights"):
        if validate_weights(list(weights.values())):
            st.success("Weights are valid!")
        else:
            st.error("The total of all weights must equal 1. Please re-enter the values.")
            # Clear session state for weights to allow re-input
            for factor in factors:
                del st.session_state[f"weight_{factor}"]

# Step 3: Provide Sub-Value Mappings
if uploaded_file and validate_weights(list(weights.values())):
    st.header("Step 3: Provide Sub-Value Mappings")
    st.write(
        "Provide the sub-values for each factor. "
        "Enter numeric values for Min, Max, and Score."
    )

    sub_value_mappings = {}

    for factor in factors:
        st.subheader(f"Sub-Values for {factor}")
        st.write("Example: Min: 0, Max: 100, Score: 50")
        
        ranges = []
        with st.container():
            for i in range(3):  # Create 3 default input rows for each factor
                cols = st.columns([1, 1, 1])
                min_val = cols[0].text_input(f"{factor} Min", placeholder="e.g., 0", key=f"min_{factor}_{i}")
                max_val = cols[1].text_input(f"{factor} Max", placeholder="e.g., 100", key=f"max_{factor}_{i}")
                score_val = cols[2].text_input(f"{factor} Score", placeholder="e.g., 50", key=f"score_{factor}_{i}")
                if min_val and max_val and score_val:
                    ranges.append({"min": float(min_val), "max": float(max_val), "score": float(score_val)})
        sub_value_mappings[factor] = ranges

    if st.button("Submit Sub-Value Mappings"):
        valid, message = validate_sub_values(sub_value_mappings)
        if valid:
            st.success("Sub-values are valid!")
        else:
            st.error(message)

# Step 4: Calculate Scores and Display Results
if uploaded_file and validate_weights(list(weights.values())):
    if "sub_value_mappings" in locals() and st.button("Calculate Scores"):
        data["Score"] = calculate_scores(data, weights, sub_value_mappings)
        st.write("Scored Products:")
        st.dataframe(data.head(20))

        if len(data) > 20:
            csv = data.to_csv(index=False)
            st.download_button("Download Full Results", data=csv, file_name="scored_products.csv", mime="text/csv")
