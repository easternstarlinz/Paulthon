import statsmodels.api as sm

def create_ols_df(returns_df: 'Two-column DataFrame of daily returns for the stock and index') -> 'DataFrame of (stock, index) daily returns with y_hat, error, error_squared':
    """This function turns a DataFrame of daily returns for the stock and index into a DataFrame of the same daily returns now with y_hat, error, and error_squared for the OLS regression."""

    stock = returns_df.columns[0]
    index = returns_df.columns[1]
    
    ols_model = sm.OLS(returns_df[stock], returns_df[index], missing='drop')
    ols_results = ols_model.fit()

    ols_beta = ols_results.params[index]

    returns_df['y_hat'] = returns_df[index]*ols_beta
    returns_df['error'] = returns_df[stock] - returns_df['y_hat']
    returns_df['error_squared'] = returns_df['error']*returns_df['error']
    return returns_df
