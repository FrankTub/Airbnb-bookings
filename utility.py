import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Create a scatter plot function
def scatter_plot(df, kpi, column):
    '''
    INPUT
    df     - pandas dataframe 
    kpi    - the variable you're interested in as a string
    column - interval variable as a string
    
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
    
def aggr(df, kpi, column):
    '''
    INPUT
    df     - pandas dataframe 
    kpi    - the variable you're interested in as a string
    column - interval variable as a string
    
    OUTPUT
    data   - A dataframe with aggregrated mean
    '''
    return data.groupby([column]).mean()[[kpi]].reset_index()