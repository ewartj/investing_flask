#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 24 13:41:06 2022

@author: jonny
"""
from pandas import read_pickle
import yahoo_fin.stock_info as stock_info
import numpy as np

ticker = "SHEL.L"

df = stock_info.get_balance_sheet(ticker)
df = df.replace(np.nan, 0)

cash_list = df.loc['cash', :].values.tolist()
cash = cash_list[0]
print(f"cash {cash}")

total_assets_list = df.loc['totalAssets', :].values.tolist()
total_assets = total_assets_list[0]
print(f"total_assets {total_assets}")

current_assets_list = df.loc["totalCurrentAssets", :].values.tolist()
current_assets = current_assets_list[0]
print(f"current_assets {current_assets}")

try:
    goodwill_list = df.loc["goodWill", :].values.tolist()
    goodwill = goodwill_list[0]
except:
    goodwill = 0.0
print(f"goodwill {goodwill}")


total_liabilities_list = df.loc["totalLiab", :].values.tolist()
total_liabilities = total_liabilities_list[0]
print(f"totalLiab {total_liabilities}")

current_liabilities_list = df.loc["totalCurrentLiabilities", :].values.tolist()
current_liabilities = current_liabilities_list[0]
print(f"current_liabilities {current_liabilities}")


try:
    short_term_debt_list = df.loc["shortLongTermDebt", :].values.tolist()
    short_term_debt = short_term_debt_list[0]
except:
    short_term_debt = 0.0
print(f"short_term_debt {short_term_debt}")
    
try:
    long_term_debt_list = df.loc["longTermDebt", :].values.tolist()
    long_term_debt = long_term_debt_list[0]
except:
    long_term_debt = 0.0
print(f"long_term_debt {long_term_debt}")


total_liabilities_list = df.loc["totalLiab", :].values.tolist()
total_liabilities = total_liabilities_list[0]
print(f"total_liabilities {total_liabilities}")

retained_earnings_list = df.loc["retainedEarnings", :].values.tolist()
retained_earnings = retained_earnings_list[0]
print(f"retained_earnings {retained_earnings}")

common_stock_list = df.loc["commonStock", :].values.tolist()
common_stock = common_stock_list[0]
print(f"common_stock {common_stock}")

capital_surplus_list = df.loc["capitalSurplus", :].values.tolist()
capital_surplus = capital_surplus_list[0]
print("CapitalSurplus:")
print(capital_surplus)


df2 = stock_info.get_cash_flow(ticker)
df2 = df2.replace(np.nan, 0)

net_income_list = df2.loc["netIncome", :].values.tolist()
net_income = net_income_list[0]
print(f"net_income {net_income}")


dep_list  = df2.loc["depreciation", :].values.tolist()
dep = dep_list[0]
print(f"dep {dep}")

capex_list = df2.loc["capitalExpenditures", :].values.tolist()
capex = abs(capex_list[0])
print(f"capex {capex}")

#FCFF

try:
    working_capital = (current_assets_list[1]  - current_liabilities_list[1]) - (current_assets_list[0] - current_liabilities_list[0])
    y = current_assets_list[0] - current_liabilities_list[0]
    z = current_assets_list[1] - current_liabilities_list[1]
    print(y)
    print(z)
except:
    working_capital = current_assets_list[0]- current_liabilities_list[0]


#working_capital=Default_Spread = float(input("Enter working capital: ")) #for when theres only one number in the list
#working_capital=working_capital * 1000
print("working capital")
print(working_capital)

# FCFF = net_income_list[0] - (abs(capex_list[0]) + working_capital)

reinvestment_rate = (abs(capex_list[0]) + working_capital) / net_income_list[0]
FCFF = net_income_list[0] * (100 - reinvestment_rate)

print('Reinvestment rate =')
print(reinvestment_rate)

print('FCFF=')
print(FCFF)

# Cost of Capital
df3 = stock_info.get_income_statement(ticker)
df3 = df3.replace(np.nan, 0)

basic_stats = stock_info.get_quote_table(ticker)

shares = basic_stats['Volume']

interest_list = df3.loc["interestExpense", :].values.tolist()
interest = abs(interest_list[0])
print(f"interest {interest}")

if interest == 0:
    interest_coverage = 13 # why this- ITS above the default spread (check still correct)
else:
    interest_coverage = net_income_list[0] / interest

print('interest coverage =')
print(interest_coverage)

metrics_dict = stock_info.get_quote_table(ticker)
beta = metrics_dict["Beta (5Y Monthly)"]
print(f"beta {beta}")

default_spread = 0 # Probably need to update these
if interest_coverage >= 12.5:
     default_spread = 0.67
elif interest_coverage < 12.499 and interest_coverage >= 9.5:
     default_spread = 0.82
elif interest_coverage < 9.499 and interest_coverage >= 3:
     default_spread = 1.03
elif interest_coverage < 7.499 and interest_coverage >= 6:
     default_spread = 1.14
elif interest_coverage < 5.999 and interest_coverage >= 4.5:
     default_spread = 1.29
elif interest_coverage < 4.499 and interest_coverage >= 4:
     default_spread = 1.59
elif interest_coverage < 3.999 and interest_coverage >= 3.5:
     default_spread = 1.93
elif interest_coverage < 3.499 and interest_coverage >= 3:
     default_spread = 2.15
elif interest_coverage < 2.999 and interest_coverage >= 2.5:
     default_spread = 3.15
elif interest_coverage < 2.499 and interest_coverage >= 2:
     default_spread = 3.78
elif interest_coverage < 1.999 and interest_coverage >= 1.5:
     default_spread = 4.62
elif interest_coverage < 1.499 and interest_coverage >= 1.25:
     default_spread = 7.76
elif interest_coverage < 1.249 and interest_coverage >= 0.8:
     default_spread = 8.8
elif interest_coverage < 0.799 and interest_coverage >= 0.5:
     default_spread = 10.76
else:
     default_spread = 14.34

#Default_Spread = float(input("Enter Default Spread: "))
print(f"default spread {default_spread}")

risk_free_rate = 1.25 # this is UK BoE interest rate can I get this from an API
equity_risk_premium = 6 # is ther an API to get this?
# equity = retained_earnings_list[0] + common_stock_list[0] + capital_surplus_list[0]
share_price = stock_info.get_live_price(ticker)
equity = share_price * shares
print(f"equity {equity}")
debt = short_term_debt + long_term_debt

cost_of_equity = risk_free_rate + beta * equity_risk_premium
print('Cost of Equity =')
print(cost_of_equity)

tax = 0.20 # put in config

cost_of_debt = (risk_free_rate + default_spread) * (1 - tax)
print('Cost of Debt =')
print(cost_of_debt)

equity_and_debt = equity + debt


weighed_d = cost_of_debt * (float(debt) / equity_and_debt)


weighed_e = cost_of_equity * (float(equity) / equity_and_debt)


weighed_capital = weighed_e + weighed_d #float(cost_of_equity) * weighed_c
print('Weighted Cost of Capital =')
print(weighed_capital)

weighed_debt = float(cost_of_debt) * weighed_d
print('Weighted Cost of Debt =')
print(weighed_debt)

cost_of_capital = (float(weighed_capital) + float(weighed_debt)) / 100
print('Cost of Capital =')
print(cost_of_capital)

# Predicting growth

todays_income = net_income_list[0]




# reinvestment_rate = (float(retained_earnings_list[0]) / float(net_income_list[0])) # is this correct?
# reinvestment_rate = float(reinvestment_rate) / 100
# reinvestment_rate = abs(reinvestment_rate)


gross_profit_list = df3.loc["grossProfit", :].values.tolist()
def calculate_growth_rate(gross_profit_list):
    two_yrs_ago = (gross_profit_list[2] - gross_profit_list[3]) / gross_profit_list[3]
    one_yr_ago = (gross_profit_list[1] - gross_profit_list[2]) / gross_profit_list[2]
    this_yr= (gross_profit_list[0] - gross_profit_list[1]) / gross_profit_list[1]
    avg = (two_yrs_ago + one_yr_ago + this_yr) / 3
    return avg

growth_rate = calculate_growth_rate(gross_profit_list)
print(growth_rate)

# growth_rate = float(growth_rate) * 100
print(f"growth rate {growth_rate}")

# Calculating terminal value

roc = net_income_list[0] / (total_assets_list[0] - current_liabilities_list[0])
print(f"ROC = {roc}")


operating_earnings = net_income_list[0]

years = 5

def pred_future_growth(operating_earnings, growth_rate, reinvestment_rate, years):
    future_income_lst = [operating_earnings]
    reinvestment_lst = []
    fcff_lst = []
    if len(future_income_lst) == 1:
        op_inc = operating_earnings * (1 + growth_rate)
        reinv = op_inc * reinvestment_rate
        fcff = op_inc - reinv
        future_income_lst.append(op_inc)
        reinvestment_lst.append(reinv)
        fcff_lst.append(fcff)
    for year in range(years - 1):
        op_inc = future_income_lst[-1] * (1 + growth_rate)
        reinv = reinvestment_lst[-1] * reinvestment_rate
        fcff = op_inc - reinv
        future_income_lst.append(op_inc)
        reinvestment_lst.append(reinv)
        fcff_lst.append(fcff)
    future_earnings = {
                        "income": future_income_lst,
                        "reinvestment": reinvestment_lst,
                        "fcff": fcff_lst
                        }
    return future_earnings

reinvestment_rate = reinvestment_rate / 100

future_earnings = pred_future_growth(operating_earnings, growth_rate, reinvestment_rate, years)
print(future_earnings)

terminal_cashflow = future_earnings["fcff"][-1]

stable_reinv_rate = (growth_rate / roc) / 100
print(f"stable_reinv_rate {stable_reinv_rate}")

terminal_value = terminal_cashflow * (1 + growth_rate) * (1 - stable_reinv_rate) / cost_of_capital - growth_rate

discounted_terminal_value = (future_earnings["fcff"][1] / (1 + cost_of_capital)) + (future_earnings["fcff"][2] / (1 + cost_of_capital)) + (future_earnings["fcff"][3] / (1 + cost_of_capital))  
+ (future_earnings["fcff"][4] + terminal_value) / (1 + cost_of_capital)


# #growth_rate = growth_rate
# delta = 2 #int(input("How many years would you like to look ahead? 3[1] or 5[2] or 10[3] "))
# #delta = delta - 1
# year = 0
# total = 0

# while year <= delta:
#     year = delta + 1
# #1
#     o1 = operating_earnings + (operating_earnings *(1 + growth_rate))
# #    o2 = o1 + (o1 - (o1 * float(Reinvestment_rate)))*(1 + growth_rate)
#     o2 = o1 + (o1 *(1 + growth_rate))
#     o3 = o2 + (o2 *(1 + growth_rate))
#     o4 = o3 + (o3 *(1 + growth_rate))
#     o5 = o4 + (o4 *(1 + growth_rate))
#     o6 = o5 + (o5 *(1 + (growth_rate)))
#     o7 = o6 + (o6 *(1 + (growth_rate)))
#     o8 = o7 + (o7 *(1 + (growth_rate)))
#     o9 = o8 + (o8 *(1 + (growth_rate)))
#     o10 = o9 + (o9 * (1 + (growth_rate)))
#     operating_earnings = o10 * (1 + (growth_rate))
#     pupils_dictionary = {}
#    for x in year(delta):
#        new_key = year + 1
#        new_age = operating_earnings
#        pupils_dictionary[new_key] = new_age
    # year = delta + 1

# if delta == 1:
#     total = o1 + o2 + o3
# elif delta == 2:
#     total = o1 + o2 + o3 + o4 + o5
# else:
#     total = o1 + o2 + o3 + o4 + o5 + o6 + o7 + o8 + o9 + o10

# print(total)
# reinvestment_rate = reinvestment_rate / 100
# terminal_value = (float(operating_earnings * (1 - reinvestment_rate))) / (float(cost_of_capital - growth_rate))

# total = total + terminal_value
# print("terminal value:")
# print(f"total {total}")

total = discounted_terminal_value + cash_list[0] - (short_term_debt + long_term_debt)

# Minority
try:
    minority_list= df.loc["minorityInterest", :].values.tolist()
    minority = minority_list[0]
except:
    minority = 0
print(f"minority {minority}")

if minority > 0.000001:
    total = total - minority_list[0]

value_company = total + cash_list[0]
print(value_company)

if debt > 0.000001:
    value_company = value_company - debt

value_company = value_company / 100 #yahoo does thinsg in cents and pence
#value_company  = abs(value_company)

print("value of Company")
print(value_company )

# size = input("K[1], mill[2] or bill[3]?")
# if size == 1:
#     Value_Company = Value_Company / 1000
# if size == 2:
#     Value_Company = Value_Company / 1000000
# if size ==
#     Value_Company = Value_Company / 1000000000


value_per_share = float(value_company) / shares

print("Value Per Share:")
print(value_per_share)
