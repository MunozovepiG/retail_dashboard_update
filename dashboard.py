import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go

excelFile = 'onboarding.xlsx'
sheetName = 'clientsOnboarding'
color='#DD133D'
colorScheme= ['#850C24', '#DD133D', '#CFCDCD', '#F99211', ]
image= 'graph.png'

dataset = pd.read_excel(excelFile, sheet_name=sheetName, usecols='A:U', header=0)
css = f"""
<style>
    .multiselect-container .multiselect-selected-label {{
        color: {color} !important;
    }}
</style>
"""


st.markdown(css, unsafe_allow_html=True)

# Set the default date range to the minimum and maximum dates from the "Creation Date" column
default_start_date = dataset['Creation Date'].min().date()
default_end_date = dataset['Creation Date'].max().date()

segment = dataset['Market Segment Description'].unique().tolist()
ages = dataset['Age'].unique().tolist()
onboardingType = dataset['Customer On Boarding Type'].unique().tolist()

## The chart of all the segments
segmentSet = pd.read_excel(excelFile, sheet_name=sheetName, usecols='W:X', header=0, nrows=10)
pie_chart = px.pie(segmentSet, title='Account per Retail Segment', values='Accounts', names='Retail sgement')
pie_chart.update_traces(marker=dict(colors=colorScheme))


##image 
st.image(image, caption="", use_column_width=False)

# Main Heading
st.title("Data breakdown of account openining trends in MCB Retail Segment")

# Other content
st.write("Please note this was last updated 26.June 2023.")
# Subheading
st.subheader("01. Overview of the accounts opened from 4th of January 2022 to 31st May 2023 ")



# Display the pie chart
st.plotly_chart(pie_chart)

st.subheader("02. A breakdown of account opening ")

# Allow the user to select the date range
start_date = st.date_input("Select Start Date", default_start_date, key="start_date_input", min_value=default_start_date, max_value=default_end_date)
end_date = st.date_input("Select End Date", default_end_date, key="end_date_input", min_value=default_start_date, max_value=default_end_date)

start_datetime = datetime.combine(start_date, datetime.min.time())
end_datetime = datetime.combine(end_date, datetime.max.time())

segment_selection = st.multiselect('Market Segment Description:', segment, default=segment)
onboarding_type = st.multiselect('Customer On Boarding Type', onboardingType, default=onboardingType)
age_selection = st.slider('Age', min_value=int(min(ages)), max_value=int(max(ages)), value=(int(min(ages)), int(max(ages))), step=1)

# Convert "Creation Date" column to datetime format
dataset['Creation Date'] = pd.to_datetime(dataset['Creation Date'], format='%d %b %Y')

# Filter the dataset based on the selected options
mask = (
   dataset['Market Segment Description'].isin(segment_selection) &
   dataset['Customer On Boarding Type'].isin(onboarding_type) &
   dataset['Age'].between(*age_selection) &
   dataset['Creation Date'].between(start_datetime, end_datetime)
)
filtered_dataset = dataset[mask]

# Calculate the number of accounts
number_of_accounts = filtered_dataset.shape[0]

# Display the number of accounts
st.markdown(f'*Number of Accounts: {number_of_accounts}*')

# Group the filtered dataset by market segment description and count the number of accounts
dataset_grouped = filtered_dataset.groupby('Market Segment Description').size().reset_index(name='Number of Accounts')

# Display the grouped data as a table
st.table(dataset_grouped)

# Create the bar chart
bar_chart = px.bar(
   dataset_grouped,
   x='Market Segment Description',
   y='Number of Accounts',
   color='Market Segment Description',
   template='plotly_white'
)

# Configure the chart
bar_chart.update_traces(marker_color=color)


# Display the bar chart
st.plotly_chart(bar_chart)

st.subheader("03. Monthly account opening")


# Month by month breakdown
# Convert "Creation Date" column to datetime format
dataset['Creation Date'] = pd.to_datetime(dataset['Creation Date'], format='%d %b %Y')

# Add a new column for month and year
dataset['Month_Year'] = dataset['Creation Date'].dt.strftime('%B %Y')

# Filter the dataset for the year 2022 and 2023
filtered_dataset['Year'] = filtered_dataset['Creation Date'].dt.year
filtered_dataset = filtered_dataset[(filtered_dataset['Year'] == 2022) | (filtered_dataset['Year'] == 2023)]

# Group the filtered dataset by month and year and count the number of accounts
dataset_grouped_monthly = filtered_dataset.groupby(filtered_dataset['Creation Date'].dt.to_period('M')).size().reset_index(name='Number of Accounts')
dataset_grouped_monthly['Month_Year'] = dataset_grouped_monthly['Creation Date'].dt.strftime('%B %Y')

# Allow the user to select the years to filter
selected_years = st.multiselect('Select Years', ['2022', '2023', '2022 & 2023'], default=['2022 & 2023'])

# Filter the dataset based on the selected years
if '2022 & 2023' in selected_years:
   filtered_dataset_selected_years = filtered_dataset
else:
   filtered_dataset_selected_years = filtered_dataset[filtered_dataset['Year'].isin([int(year) for year in selected_years])]

# Group the filtered dataset by month and year and count the number of accounts
dataset_grouped_selected_years = filtered_dataset_selected_years.groupby(filtered_dataset_selected_years['Creation Date'].dt.to_period('M')).size().reset_index(name='Number of Accounts')
dataset_grouped_selected_years['Month_Year'] = dataset_grouped_selected_years['Creation Date'].dt.strftime('%B %Y')

# Display the grouped data as a table
st.table(dataset_grouped_selected_years[['Month_Year', 'Number of Accounts']])

# Create a figure for the plot
fig = go.Figure()

# Add a bar trace for the number of accounts per month

fig.add_trace(go.Bar(
   x=dataset_grouped_selected_years['Month_Year'],
   y=dataset_grouped_selected_years['Number of Accounts'],
   name='Number of Accounts',
   marker_color=color))

# Configure the figure layout
fig.update_layout(
   title='Total Number of Accounts Opened per Month',
   xaxis_title='Month and Year',
   yaxis_title='Number of Accounts',
   barmode='group'
)

# Display the figure at the bottom
st.plotly_chart(fig)


st.subheader("04. Generation breakdown and Juice usage")



## the generation GENERATIONS 
# Create the multiselect filter for segment selection
segment_selection = st.multiselect('Select Market Segment:', dataset['Market Segment Description'].unique(), default=['MASS'])


# Filter the dataset based on the selected date range and market segment description
filtered_dataset = dataset[
    (dataset['Creation Date'] >= start_datetime) &
    (dataset['Creation Date'] <= end_datetime) &
    (dataset['Market Segment Description'].isin(segment_selection))
]

# Calculate the percentage of generations within the filtered dataset
generation_percentage = filtered_dataset['Generation'].value_counts(normalize=True) * 100

# Create the bar chart
bar_chart = px.bar(
    generation_percentage,
    x=generation_percentage.index,
    y=generation_percentage.values,
    labels={'x': 'Generation', 'y': 'Percentage'},
    template='plotly_white'
)

# Configure the chart
bar_chart.update_traces(marker_color=color)

# Display the bar chart
st.plotly_chart(bar_chart)


####MCB Juice

# Calculate the number of accounts
filtered_dataset['Has Juice'] = filtered_dataset['No. of days between CIR creation and Juice Subscription'].notnull()
juice_percentage = filtered_dataset['Has Juice'].value_counts(normalize=True) * 100

# Create a bar chart for the percentage of users with Juice
juice_bar_chart = px.bar(
    x=['Has Juice', 'No Juice'],
    y=juice_percentage.values.tolist(),  # Convert the Pandas Series to a list
    labels={'x': 'Has Juice', 'y': 'Percentage'},
    template='plotly_white'
)

# Configure the chart
juice_bar_chart.update_traces(marker_color=color)

# Display the bar chart for the percentage of users with Juice
st.plotly_chart(juice_bar_chart)
