import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Create a scatter plot function
def scatter_plot(df, kpi, column, plt):
    '''
    INPUT
    df     - pandas dataframe
    kpi    - the variable you're interested in as a string
    column - interval variable as a string
    plt    - subplot

    OUTPUT
    X      - A scatter plot, with on the  x-axis the column and on the y-axis the kpi.
    '''
    plt.scatter(x=df[column], y=df[kpi])
    plt.xlabel(column)
    plt.ylabel(kpi)
    return plt

def clean_data(df):
    '''
    INPUT
    df - pandas dataframe containing info from the license.csv file

    OUTPUT
    df - cleaned dataframe, removed unnecassary columns
    '''
    data = df.copy()
    # Drop columns which have no added value.
    data.drop(['square_feet', 'host_total_listings_count', 'id', 'scrape_id', 'host_id', 'latitude', 'longitude', 'license'], axis=1, inplace=True)
    # Get overview of how many unique values a column has.
    s = data.nunique()
    unique_data = pd.DataFrame({'column':s.index, 'unique_values':s.values})

    # Drop all columns that have a single value
    for idx, row in unique_data.iterrows():
        if row.unique_values == 1:
            data.drop([row.column], axis=1, inplace=True)

    # The pricing column contains all prices in dollars, but these are stored as an object. First we need to remove the $
    cols_to_check = ['price', 'weekly_price', 'monthly_price', 'security_deposit', 'cleaning_fee', 'extra_people']
    for col in cols_to_check:
        data[col] = data[col].apply(lambda x : x[1:].replace(",", "") if str(x).startswith("$") else x)
    # Then we need to cast these columns to float.
    data[cols_to_check] = data[cols_to_check].astype(float)

    # First make sure we have a weekly_price in all columns
    data['weekly_price'] = data.apply(
        lambda row: row['price']*7 if np.isnan(row['weekly_price']) else row['weekly_price'],
        axis=1
    )

    # Next, we make sure that we a monthly_price in all cases
    data['monthly_price'] = data.apply(
        lambda row: row['weekly_price']*4.34524 if np.isnan(row['monthly_price']) else row['monthly_price'],
        axis=1
    )

    return data

def clean_calendar_data(df):
    '''
    INPUT
    df - pandas dataframe containing info from the calendar.csv file

    OUTPUT
    df - aggregrated dataframe containing occupancy rate per day
    '''
    data_calendar = df.copy()
    # Make sure we only take the rows where the appartment was booked, then group by on date and count how many houses where booked
    data_calendar = df_calendar[df_calendar['available'] == 'f'].groupby('date').count()['listing_id'].reset_index()
    # Then divide that number by the total number of houses in the dataset
    data_calendar['listing_id'] = data_calendar['listing_id'] / df_calendar.listing_id.nunique()
    # Rename the columns
    data_calendar.columns = ['date', 'occupancy_rate']
    # Cast the datatype of the date column so that we can use plot_date.
    data_calendar['date'] = pd.to_datetime(data_calendar['date'])

    return data_calendar

def aggr(df, kpi, column):
    '''
    INPUT
    df     - pandas dataframe
    kpi    - the variable you're interested in as a string
    column - interval variable as a string

    OUTPUT
    data   - A dataframe with aggregrated mean
    '''
    return df.groupby([column]).mean()[[kpi]].reset_index()