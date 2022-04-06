### Calculating Excess Returns ###
##################################

"""
Source: https://sites.google.com/view/jingcynthiawu/yield-data
Download date (most recent update): March 24, 2022 
Data source: Yan Liu and Jing Cynthia Wu, "Reconstructing the Yield Curve", Journal of Financial Economics, 2021, 142 (3), 1395-1425. 

Data annotation: 
    "Annualized continuously-compounded zero-coupon yields in percentage points. Each column corresponds to a maturity between 1 to 360 months." 
"""


### Libraries 
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os


## Load in Data --> YIELDS
""" 
    -- Date (first column): June 1961 to December 2019 in "YYYYMM""
    -- Data: Annualized continuously-compounded zero-coupon yields in percentage points. 
            --> Each column corresponds to a maturity between 1 to 360 months         
    -- Main Paper:
        --> We denot its (log) price and (continuously compounded) yield at t by p_{t}^{n} and y_{t}^{n} = - 1/n * p_{t}^{n}
"""
os.chdir("/home/freddy/Dropbox/Thesis_Final/Data/")
yields = pd.read_excel("YieldCurve/LW_monthly_March.xlsx")
yields = yields.drop(yields.index[0:7], axis=0)
yields.columns = yields.iloc[0,:]
yields = yields.drop(yields.index[0], axis=0)
yields = yields.rename(columns = {yields.columns[0]: "date"})

# Change DateFormat
yields.iloc[:,0] = [pd.to_datetime(yields.iloc[x,0], format = "%Y%m") for x in range(len(yields))] # NEW
yields = yields.set_index(yields.columns[0])

# Rename Columns
yields.columns = yields.columns.str.replace("m","")
yields.columns = yields.columns.str.replace(" ","")
yields.columns = "m" + yields.columns


"""
from: https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr884.pdf
"... using monthly and quarterly data on zero-coupon yields expressed in annualized percent obtained from Liu and Wu (2019)..."
"""

# Reduce Data to yields of between 1 and 10 years (only full years)
    # !!! Possibility of adding intra-year data (i.e., 13 or 14 months)
    # !!! Possibility of adding summary statistics for different maturities (possibly combined summary statistics of longer-term maturities)
        # e.g.: Distribution of past returns compared to current returns (deviation from mean or extreme divergence...)
        # --> Many ways with which to make use of the data instead of throwing out
yields = yields.loc[:,[yields.columns[x] for x in range(11,121,12)]]


# Reduced yields
    # Drop all data before 1971-08
    # Compress data to only yearly observations (i.e., 12, 24... months)
    # --> range(12,132,12)
yields = yields.dropna()
yields = yields.loc[:,["m" + str(month) for month in range(12,132,12)]]


# From Liu (2021) --> page 1403
""" 
    Define the zero-coupon yield at t with a maturity of n as y(t,n). The price of the n-year discount bond 
    at time t relates to the zero-coupon yield as follows:
        
            log(P(t,n)) = - n * y(t,n) 
        
    where n is maturiy in years as in CP. The forward rate with maturity n at time t is defined as the 
    return for a loan starting at t+n-1 and maturing at t+n

            f(t,n) = log(P(t,n-1)) - log(P(t,n))
            
    The holding-period return of buying an n-period bond and selling it one year later is:
        
            r(t+1,n) = log(P(t+1,n-1)) - log(P(t,n)) --> beware t+1  means +12 months
            
    The excess return is:
        
            rx(t+1,n) = r(t+1,n) - y(t,1) --> again, +12 months
            
    where y(t,1) is the one-year risk-free rate. 
"""

# Log prices (and prices)
log_prices = yields.copy()
prices = yields.copy()
for _t,_y in enumerate(yields.columns):
    # log prices --> Shorter: log_prices[_y] = - (_t+1) * yields[_y]/100    
    _series = - (_t+1) * yields[_y]/100
    _series = _series.values.astype(float)
    log_prices[_y] = _series
    prices[_y] = np.exp(_series)


# one-year implied forward rate
fwd_rates = log_prices.shift(+1, axis=1) - log_prices
fwd_rates["m12"] = -log_prices["m12"]
fwd_rates.columns = fwd_rates.columns.str.replace("m","f")



# holding-period return of buying an n-period bond and selling it one year later
""" remember:
        - The holding-period return of buying an n-period bond and selling it one year later is:
                r(t+1,n) = log(P(t+1,n-1)) - log(P(t,n))
                    --> !!! IMPORTANT: consider the t+1
                        --> realized in that period! (target of forecast)
                        
        --> first entry in dataframe @ 1972-08-01
        --> holding-period return realized from buying an n-period bond at 1971-08-01
            and selling it one year later in 1972-08-01
            
                --> Hence, forecast for first return needs to be made with information available
                    at or prior to 1971-08-01

(The holding-period return for a one-year discount bond is simply the negative of the logprice for (p(t,1))))
"""
hold_return = pd.DataFrame(index = log_prices.index, columns = log_prices.columns)
for _c in range(1, log_prices.shape[1]):  
    for _t in range(12, log_prices.shape[0],1):
        hold_return.iloc[_t,_c] = log_prices.iloc[_t,_c-1] - log_prices.iloc[_t-12,_c]    



# Excess returns
"""
Excess return: 
    -->  rx(t+1,n) = r(t+1,n) - y(t,1)
        --> where y(t+1,n) is the one-year risk-free rate

(excess return for discount bonds of n=1; log(P(t,1))-y(t,1) --> 0)
"""
xr = pd.DataFrame(index = hold_return.index, columns = hold_return.columns)
for _t in range(12, log_prices.shape[0],1):
    _yields = yields.iloc[_t-12,0]/100
    for _c in range(1, log_prices.shape[1]):
        xr.iloc[_t,_c] = hold_return.iloc[_t,_c] - _yields


# rename columns
xr.columns = xr.columns.str.replace("m","xr")

# drop xr12 --> contains non information
xr = xr.drop("xr12", axis=1)





###############################################################################################################################
###############################################################################################################################


##############################################################################
## Macrod Data Set ## Macrod Data Set ## Macrod Data Set ## Macrod Data Set ##
 
"""
Data source: https://research.stlouisfed.org/econ/mccracken/fred-databases/
Last updated: March 26, 2022
Data name: 2022-02.csv
Data type: quarterly data
"""

# Load in Data --> Macro Variables
macro = pd.read_csv("MacroData/2022-02.csv")


# get rid of "Transform" and change index and date-format
macro = macro.drop(macro.index[0], axis = 0)
macro.sasdate = [pd.to_datetime(macro.sasdate[t], infer_datetime_format = True) for t in macro.index]
macro = macro.set_index("sasdate", drop = True)
macro = macro.drop(macro.index[-1])


# adjust index
_begin, _end = xr.index[0], xr.index[-1]
macro = macro.loc[_begin:_end,:]


# nan values
"""
Which values are missing (relevant number of missings):
    - for the relevant time horizon:
        i) ACOGNO: 246 observations missing (out of 605)
        ii) TWEXAFEGSMTHx: 17
        iii) UMCSENTx: 51
    
"""
# drop column
macro = macro.drop("ACOGNO", axis=1)

# !!! fill nan !!!
macro = macro.fillna(method = "ffill")

# !! TWEXAFEGSMTHx <-- only missing up until 1973 
    # not corrected with ffill due to it missing up UNTIL 1973 with no prior values
    # !!! Fix with: fill with first actual value (back-date/log)
    # first value @ 1973-01-01 --> use this one
macro.TWEXAFEGSMTHx[:"1973-01-01"] = macro.TWEXAFEGSMTHx["1973-01-01"]



###############################################################################################################################
###############################################################################################################################

"""
Change the column names so that lgbm does not end in error message
    --> remove special characters and remove spaces
"""
macro.columns = [macro.columns[_k].replace("&", "_and_") for _k in range(macro.shape[1])]
macro.columns = [macro.columns[_k].replace(" ", "_") for _k in range(macro.shape[1])]
macro.columns = [macro.columns[_k].replace(":", "") for _k in range(macro.shape[1])]


######################
## Combine Datasets ##
"""
Make multiple datasets:
    Dataset1: contains only forward rates and excess return (Application 1)
    Dataset2: contains forward rates, excess returns and macro data (Application 2)
    Dataset3: contains forward rates, excess returns, macro data and conflict data
"""

###########
## Dataset1:
"""
includes forward rates and excess returns
        # --> first realized excess returns at: 1972-08-01
        # --> first prediction can be made at: 1971-08-01
        # combine so that data with which to predict and the target (realized excess return) are in same row 
        
last prediction/excess return:
        # given that fwd_rates data ends at 2021-12-01:
            --> last verifiable excess return can be forecast at 2020-12-01 (since one-year excess return)
                where the last realized excess return is at 2021-12-01
"""


# concat on the shifted xr dataset (correct by 12 months)
dataset1 = pd.concat([xr.shift(-12,axis=0), fwd_rates], axis=1)

# drop last 12 rows of the dataframe
dataset1 = dataset1.drop(dataset1.index[-12:], axis=0)



############
## Dataset2:
"""
includes forward rates, excess returns and macro data:
    # changes nothing of start_date of dataframe
"""

# concat all 3 elements
dataset2 = pd.concat([xr.shift(-12,axis=0), fwd_rates, macro], axis=1)

# drop last 12 rows of the dataframe
dataset2 = dataset2.drop(dataset2.index[-12:], axis=0)


############
## Dataset3:
"""
includes forward rates, excess returns, macro and conflict data:
    
"""


###############################################################################################################################
###############################################################################################################################


###########################
### Save the Dataframes ###
import xlsxwriter
writer = pd.ExcelWriter("/home/freddy/Dropbox/Thesis_Final/prepared_data/dataset1_2.xlsx", engine="xlsxwriter")
dataset1.to_excel(writer, sheet_name = "dataset1")
dataset2.to_excel(writer, sheet_name = "dataset2")
writer.save()


