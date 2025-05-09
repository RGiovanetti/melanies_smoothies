# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for order name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Snowflake connection
cnx = st.connection('snowflake')
session = cnx.session()

# Get fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Show fruit selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# If ingredients selected and name provided
if ingredients_list and name_on_order:
    ingredients_string = ', '.join(ingredients_list)

    # Show nutrition info for each fruit
    for fruit_chosen in ingredients_list:
        search_row = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen]
        if not search_row.empty:
            search_on = search_row['SEARCH_ON'].iloc[0]
            st.subheader(f"{fruit_chosen} Nutrition Information")
            try:
                response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
                if response.ok:
                    st.dataframe(data=response.json(), use_container_width=True)
                else:
                    st.error(f"Could not fetch info for {fruit_chosen}.")
            except Exception as e:
                st.error(f"Error fetching data for {fruit_chosen}: {e}")

    # Insert into orders table
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

