# -*- coding: utf-8 -*-
"""app

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1KJwbu3GiSFgcLRRyi5AEN2e08w5Fl3Ma

**Using OpenAI API Key to generate synthetic data**
"""

import openai

openai.api_key ='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'

import time
time.sleep(1)

""" STATE | COUNTY | VALUE | SUBCATEGORY Data"""

import pandas as pd
import json
import io
import re

def extract_json_part(response_text):

    # Regular expression to match JSON arrays
    json_match = re.search(r'\[\s*\{.*?\}\s*\]', response_text, re.DOTALL)

    if json_match:
        json_data = json_match.group(0)  # Extract the JSON part
        try:
            return json.loads(json_data)  # Parse JSON into Python object
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    else:
        print("No valid JSON array found in the response.")
        return None

# Define the prompt for synthetic data
def generate_synthetic_data(num_rows, subcategory):
    prompt = """Generate synthetic data of {num_rows} observations with the following columns, Do not truncate the data, give complete data.:
    - State: Only U.S. states.
    - County: Real counties within the states.
    - Value: Random numerical data with a variance close to 1.
    - Subcategory: {subcategory}

    Please output the data as a JSON array with each row as an object. The JSON format should look like this:
    [
        {"state": "State Name", "county": "County Name", "value": some_number, "subcategory": "Some Category"},
        ...
    ]"""

    # Make the API call
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a data analyst expert and will provide JSON formatted data"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=5000,
        temperature=0
    )
    # Extract and parse the response content
    response_text = response.choices[0].message.content

    # Extract JSON array using regex and remove '...'
    data = extract_json_part(response_text)

    if data:
        return pd.DataFrame(data)  # Convert JSON data to DataFrame
    else:
        return None

import streamlit as st
# Streamlit app
st.title("Synthetic Data Generator")

# Input fields for user to specify parameters
num_rows = st.number_input("Number of rows", min_value=10, max_value=1000, value=100)
subcategory = st.text_input("Subcategory (e.g., Health, Education, etc.)", "Health")

if st.button("Generate Data"):
    with st.spinner("Generating synthetic data..."):
        # Call the function to generate synthetic data
        df = generate_synthetic_data(num_rows, subcategory)

        if df is not None:
            # Display the generated data
            st.write("Generated Data:")
            st.dataframe(df)

            # Convert DataFrame to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Synthetic Data')
                writer.close()
            output.seek(0)

            # Provide download button for the Excel file
            st.download_button(
                label="Download data as Excel",
                data=output,
                file_name="synthetic_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Failed to generate data. Please try again.")