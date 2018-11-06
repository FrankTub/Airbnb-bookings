import matplotlib.pyplot as plt

# Create a scatter plot function
def scatter_plot(df, kpi, column) :
    '''
    INPUT
    df     - pandas dataframe 
    kpi    - the variable you're interested in
    column - interval variable
    
    OUTPUT
    X - A scatter plot, with on the  x-axis the column and on the y-axis the kpi.
    '''
    plt.scatter(x=df[column], y=df[kpi])
    plt.xlabel(column)
    plt.ylabel(kpi)
    return plt