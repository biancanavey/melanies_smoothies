# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title("Customise your smoothie :cup_with_straw:")
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch the fruit options from the Snowflake table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))

# Display the DataFrame in the Streamlit app
# st.dataframe(data=my_dataframe, use_container_width=True)

pd_df =my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()

# Input for the name on the smoothie order
name_on_order = st.text_input("Name on Smoothie", value="")
st.write("The name on your smoothie will be:", name_on_order)

# Multiselect for choosing ingredients
ingredients_list = st.multiselect(
    "Choose Up to 5 Ingredients:", my_dataframe['FRUIT_NAME'].tolist(), max_selections=5)

# Check if any ingredients were selected
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+ fruit_chosen)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        
    # Prepare the SQL insert statement
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                         VALUES ('{ingredients_string}', '{name_on_order}')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")

# New section to display smoothie fruit nutrition information
# smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
# if smoothiefroot_response.status_code == 200:
#     # nutrition_data = smoothiefroot_response.json()
#     # st.json(nutrition_data)  # Display the nutrition information in JSON format
#     sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
# else:
#     st.error("Failed to fetch nutrition information.")
