import streamlit as st
import pandas as pd
import glob
import os
import streamlit as st
import json

st.set_page_config(page_title="Similarweb Samples", page_icon="images/similarweb_logo_page_icon.png", layout="wide")  # Adjust layout as needed
#st.image("images/similarweb_logo.png")
st.image("images/omri_logo.webp")
st.title('Batch API Dataset Menu')
st.write("#### Choose Your Dataset, View a Sample, and Get API Code")
st.write("##### **this tool allows you to discover new data sets - please reach out to your Account Manager for access")
         
exporter = False
# Create a checkbox with a custom label for "Advanced Mode"
#exporter = st.checkbox("Exporter Datasets Only")

# Content based on the selected mode (checkbox state)
dataframes = {}
if exporter:
  st.write("Exporter Datasets")
  for file in os.listdir("datasets/exporter_datasets"):
    dataframes[file.replace(".csv","")] = pd.read_csv(f'datasets/exporter_datasets/{file}')
  tables_granularities_mapping=pd.read_csv("tables_granularities_mapping_exporter.csv")

  # Add more elements specific to advanced mode here
else:
  #st.write("Batch API Datasets")
  for file in os.listdir("datasets/bulk_api_datasets"):
    dataframes[file.replace(".csv","")] = pd.read_csv(f'datasets/bulk_api_datasets/{file}')
  tables_granularities_mapping=pd.read_csv("tables_granularities_mapping.csv")

  # Add more elements specific to amateur mode here

### read the vtables/granularity mapping
tables_granularities_dict = tables_granularities_mapping.set_index('table')['granularity'].to_dict()

exporter_tables = list(pd.read_csv("exporter_tables.csv")["table"])
exporter_tables.remove("keywords")
exporter_tables.remove("desktop_top_geo")
exporter_tables.remove("popular_pages")
exporter_tables.remove("company_info")
#st.write(exporter_tables)

if exporter:
    table_names = exporter_tables
else:
    table_names = list(tables_granularities_dict.keys())
 

all_dataframes = list(dataframes.keys())

### remove when we fix these
exclusion_list = ["apps_premium","apps_premium_affinity","subsidiaries","travel_intelligence","ticker_mapping_point_in_time",
                  "disney_total_visits","daily_display_ads","technologies","serp","ticker_mapping_feed",
                  "russel_1000_calibrated_domains","russel_1000_calibrated_tickers","russel_1000_estimated_tickers",
                  "russel_1000_tickers_domains","ticker_tracker_calibrated","google_keyword_calibrated","oss_keyword_calibrated",
                  "pvp_calibrated", "videos_calibrated"]

table_names = [table for table in table_names if table not in exclusion_list and not "s4i" in table]

apps_dataframes = [x for x in table_names if "apps" in x.lower()]
shoppers_dataframes = [x for x in table_names if "shopper" in x.lower()]
keywords_dataframes = [x for x in table_names if "keyword" in x.lower() and not "calibrated" in x.lower()]
stock_dataframes = [x for x in table_names if "ticker" in x.lower() or "russel" in x.lower()]
technology_dataframes = ["technographics"]
company_dataframes = ["website"] # add company_info and #company_funding when these are available again
other_list = list(set(table_names) - set(apps_dataframes) - set(shoppers_dataframes) - set(keywords_dataframes) -set(stock_dataframes)-set(technology_dataframes) - set(company_dataframes))

# exporter not relevant
if exporter:
    category_options = {
      "apps": apps_dataframes,
      "keywords": keywords_dataframes,
      "shopper": shoppers_dataframes,
      "others": other_list
    }
else:
  category_options = {
  "all": table_names,
  "apps": apps_dataframes,
  "company": company_dataframes,
  "keywords": keywords_dataframes,
  "shopper": shoppers_dataframes,
  "stocks": stock_dataframes,
  "technologies": technology_dataframes,
  "website": other_list
}

   
selected_category = st.selectbox("Select Entity Type", options=list(category_options.keys()))

# # Filter sub-options based on category
sub_options = category_options.get(selected_category, [])

# Dropdown menu options
dropdown_options = sorted(list(dataframes.keys()))  # Get list of dataframe names

# User selection from dropdown menu
selected_dataframe = st.selectbox("Choose vtable:", sorted(sub_options))
       
with open("api_calls_dict.json", 'r') as f:
    api_call_dict = json.load(f)
   
# Display the selected dataframe
if selected_dataframe:
    #st.write(tables_granularities_dict)
    
    for granularity in eval(tables_granularities_dict[selected_dataframe]):
        df_to_display = f'{selected_dataframe}_{granularity}'
        selected_df = dataframes[df_to_display]  # Get the chosen dataframe
        st.subheader(f"{selected_dataframe.upper()}_{granularity.upper()}", divider = "orange")
        st.dataframe(selected_df)  # Display the first 5 rows
        with st.expander("Batch API Request"):
            formatted_code = json.dumps(api_call_dict[df_to_display], indent=4)
            st.code(formatted_code, language='python')
