import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# Variable to make sure that we don't store the images for the post in the git repository.
filedir=r'C:\Users\frank_tubbing\Dropbox\Data Science\Term 2\Breaking into the field'

# Create a scatter plot function
def scatter_plot(df, kpi, column, plt, title=None):
    '''
    INPUT
    df     - pandas dataframe
    kpi    - the variable you're interested in as a string
    column - interval variable as a string
    plt    - subplot
    title  - Title of the figure

    OUTPUT
    X      - A scatter plot, with on the  x-axis the column and on the y-axis the kpi.
    '''
    plt.scatter(x=df[column], y=df[kpi])
    x = format_string(column)
    y = format_string(kpi)
    
    if title is None:
        title = x + ' vs ' + y
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(title)
    
    filepath = os.path.join(filedir, title)
    plt.savefig(filepath, bbox_inches='tight')
    return plt

def clean_data(df, df2):
    '''
    INPUT
    df - pandas dataframe containing info from the license.csv file

    OUTPUT
    df - cleaned dataframe, removed unnecassary columns
    '''
    dat = df.copy()
    df_calendar = df2.copy()
    
    # First do some group by and pivotting to get the information we need.
    df_occupied = pd.DataFrame(pd.pivot_table(df_calendar.groupby(['listing_id', 'available']).count()['date'].reset_index(),index=["listing_id"], columns='available', values='date').reset_index(), columns=['listing_id', 'f', 't']).fillna(0)
    # Then rename our columns, available(f) means that the house was occupied, available(t) means that the house was available
    df_occupied.columns = ['listing_id', 'occupied', 'available']

    # Create a column that shows how often an appartment is occupied. This will be our main value that we want to demistify
    df_occupied['occupancy_rate'] = df_occupied['occupied'] / (df_occupied['available'] + df_occupied['occupied'])

    # First I made sure that all apartments contained 365 rows in the calendar.csv and then concluded that we don't need the available and occupied column.
    # So we can remove the other unnecessary columns
    df_occupied.drop(['available', 'occupied'], axis=1, inplace=True)
    
    # Join two dataframes on listing_id
    data = dat.merge(df_occupied, left_on='id', right_on='listing_id', how='inner')
    
    # Remove the added listing_id column and availability 365, I found it easier to interpret occupancy rate!
    data.drop(['listing_id', 'availability_365'], axis=1, inplace=True)
    
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
    df_calendar = df.copy()
    # Make sure we only take the rows where the appartment was booked, then group by on date and count how many houses were booked
    data_calendar = df_calendar[df_calendar['available'] == 'f'].groupby('date').count()['listing_id'].reset_index()
    # Then divide that number by the total number of houses in the dataset
    data_calendar['listing_id'] = data_calendar['listing_id'] / df_calendar.listing_id.nunique()
    # Rename the columns
    data_calendar.columns = ['date', 'occupancy_rate']
    # Cast the datatype of the date column so that we can use plot_date.
    data_calendar['date'] = pd.to_datetime(data_calendar['date'])

    return data_calendar
    
def clean_review_data(df):
    '''
    INPUT
    df - pandas dataframe containing info from the review.csv file

    OUTPUT
    df - aggregrated dataframe containing occupancy rate per day
    '''
    df_reviews = df.copy()
    # Group by on date and count how many reviews were made on that day
    data_reviews = df_reviews.groupby('date').count()['id'].reset_index()
    # Reset the column names
    data_reviews.columns = ['date', 'num_reviews']
    # Cast the datatype of the date column so that we can use plot_date.
    data_reviews['date'] = pd.to_datetime(data_reviews['date'])

    return data_reviews

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

def format_string(str):
    '''
    INPUT
    str     - column name containing "_" charachters

    OUTPUT
    str     - Formatted string, first letter is capatilized and "_" are replaced with " "
    '''
    return str.replace("_", " ").capitalize()

def box_plot(df, kpi, column, plt, title=None):
    '''
    INPUT
    df     - pandas dataframe
    kpi    - the variable you're interested in as a string
    column - interval variable as a string
    plt    - subplot
    title  - Title of the figure

    OUTPUT
    X      - A box plot, with on the  x-axis the column and on the y-axis the kpi.
    '''
    df.boxplot(column=kpi, by=column);
    plt.suptitle('');
    x = format_string(column)
    y = format_string(kpi)
    if title is None:
        title = y + ' per ' + x
    plt.title(title);
    plt.xlabel(x);
    plt.ylabel(y);
    
    filepath = os.path.join(filedir, title)
    plt.savefig(filepath, bbox_inches='tight')
    
    return plt

def date_plot(df, column, plt, title=None):
    '''
    INPUT
    df     - pandas dataframe
    column - interval variable as a string
    plt    - subplot

    OUTPUT
    X      - A date plot, with on the  x-axis the timeframe and on the y-axis the column.
    '''
    plt.plot_date(df['date'], df[column], linestyle='solid', marker='None');
    metric = format_string(column);
    plt.ylabel(metric);
    if title is None:
        title = metric + ' over time'
    plt.title(title)
    
    filepath = os.path.join(filedir, title)
    plt.savefig(filepath, bbox_inches='tight')

    return plt
    