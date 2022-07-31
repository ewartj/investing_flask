import numpy as np
import yahoo_fin.stock_info as stock_info

class Wacc():
    def __init__(self, ticker, risk_free_rate, equity_risk_premium, tax, years_to_predict):
        self.ticker = ticker
        self.risk_free_rate = risk_free_rate
        self.equity_risk_premium = equity_risk_premium
        self.tax = tax
        self.years_to_predict = years_to_predict
        # add other variables here
    def __get_balance_sheet_variables(self, balance_sheet):
        cash_list = balance_sheet.loc['cash', :].values.tolist()
        self.cash = cash_list[0] # do i need this
        total_assets_list = balance_sheet.loc['totalAssets', :].values.tolist()
        self.total_assets = total_assets_list[0]
        self.current_assets_list = balance_sheet.loc["totalCurrentAssets", :].values.tolist()
        self.current_assets = self.current_assets_list[0]
        try:
            goodwill_list = balance_sheet.loc["goodWill", :].values.tolist()
            self.goodwill = goodwill_list[0]
        except:
            self.goodwill = 0.0
        total_liabilities_list = balance_sheet.loc["totalLiab", :].values.tolist()
        self.total_liabilities = total_liabilities_list[0]
        self.current_liabilities_list = balance_sheet.loc["totalCurrentLiabilities", :].values.tolist()
        self.current_liabilities = self.current_liabilities_list[0]
        try: # Do I need to do this with long term debut/everything?
            short_term_debt_list = self.balance_sheet.loc["shortLongTermDebt", :].values.tolist()
            self.short_term_debt = short_term_debt_list[0]
        except:
            self.short_term_debt = 0.0
        try:
            long_term_debt_list = balance_sheet.loc["longTermDebt", :].values.tolist()
            self.long_term_debt = long_term_debt_list[0]
        except:
            self.long_term_debt = 0.0
        total_liabilities_list = balance_sheet.loc["totalLiab", :].values.tolist()
        self.total_liabilities = total_liabilities_list[0]
        retained_earnings_list = balance_sheet.loc["retainedEarnings", :].values.tolist()
        self.retained_earnings = retained_earnings_list[0]
        common_stock_list = balance_sheet.loc["commonStock", :].values.tolist()
        self.common_stock = common_stock_list[0]
        capital_surplus_list = balance_sheet.loc["capitalSurplus", :].values.tolist()
        self.capital_surplus = capital_surplus_list[0]
        try:
            minority_list = balance_sheet.loc["minorityInterest", :].values.tolist()
            self.minority = minority_list[0]
        except:
            self.minority = 0
        balance_sheet.to_csv("balance_sheet.csv")
    def __get_cash_flow_variables(self, cash_flow):
        net_income_list = cash_flow.loc["netIncome", :].values.tolist()
        self.net_income = net_income_list[0]
        dep_list  = cash_flow.loc["depreciation", :].values.tolist()
        self.dep = dep_list[0]
        capex_list = cash_flow.loc["capitalExpenditures", :].values.tolist()
        self.capex = abs(capex_list[0])
        cash_flow.to_csv("cash_flow.csv")
    def __get_income_statement_variables(self, income_statement):
        interest_list = income_statement.loc["interestExpense", :].values.tolist()
        self.interest = abs(interest_list[0])
        self.gross_profit_list = income_statement.loc["grossProfit", :].values.tolist()
        income_statement.to_csv("income_statement.csv")
    def __get_quote_variables(self):    
        basic_stats = stock_info.get_quote_table(self.ticker)
        self.shares = basic_stats['Volume']
        self.share_price = stock_info.get_live_price(self.ticker)
    def __get_metrics_variables(self): 
        metrics_dict = stock_info.get_quote_table(self.ticker)
        self.beta = metrics_dict["Beta (5Y Monthly)"]
        if str(self.beta) == "nan":
            self.beta = 1
    def __get_default_spread(self, interest_coverage, default_spread_array):
        try:
            return default_spread_array[1][interest_coverage > [default_spread_array[0]]][0]
        except:
            return 14.34
    def calc_default_spread(self, interest):
        if interest == 0:
            interest_coverage = 13 # why this- ITS above the default spread (check still correct)
        else:
            interest_coverage = self.net_income / interest # net_income_list not net_income
        default_spread_array = np.array(
        [[12.5, 9.5, 7.5, 6, 4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1.25, 0.8, 0.5],
        [0.67, 0.82, 1.03, 1.14, 1.29, 1.59, 1.93, 2.15, 3.15, 3.78, 4.62, 7.78, 8.8, 10.76]])
        default_spread = self.__get_default_spread(interest_coverage, default_spread_array)
        return default_spread
    def calculate_growth_rate(self):
        two_yrs_ago = (self.gross_profit_list[2] - self.gross_profit_list[3]) / self.gross_profit_list[3]
        one_yr_ago = (self.gross_profit_list[1] - self.gross_profit_list[2]) / self.gross_profit_list[2]
        this_yr= (self.gross_profit_list[0] - self.gross_profit_list[1]) / self.gross_profit_list[1]
        avg = (two_yrs_ago + one_yr_ago + this_yr) / 3
        return avg
    def calc_cost_of_capital(self, default_spread):
        cost_of_debt = (self.risk_free_rate + default_spread) * (1 - self.tax)
        cost_of_equity = self.risk_free_rate + self.beta * self.equity_risk_premium
        equity = self.shares * self.share_price
        debt = self.short_term_debt + self.long_term_debt
        equity_and_debt = equity + debt
        weighed_d = cost_of_debt * (debt/equity_and_debt)
        weighed_e = cost_of_equity * (equity/equity_and_debt)
        weighed_capital = weighed_e + weighed_d
        weighed_debt = float(cost_of_debt) * weighed_d
        cost_of_capital = (float(weighed_capital) + float(weighed_debt)) / 100
        return cost_of_capital
    def calc_working_capital(self):
        try:
            working_capital = (self.current_assets_list[1]  - self.current_liabilities_list[1]) - (self.current_assets_list[0] - self.current_liabilities_list[0])
        except:
            working_capital = self.current_assets_list[0]- self.current_liabilities_list[0]
        return working_capital
    def pred_future_growth(self, growth_rate, reinvestment_rate):
        future_income_lst = [self.net_income]
        reinvestment_lst = []
        fcff_lst = []
        if len(future_income_lst) == 1:
            op_inc = self.net_income * (1 + growth_rate)
            reinv = op_inc * reinvestment_rate
            fcff = op_inc - reinv
            future_income_lst.append(op_inc)
            reinvestment_lst.append(reinv)
            fcff_lst.append(fcff)
        for year in range(self.years_to_predict - 1):
            op_inc = future_income_lst[-1] * (1 + growth_rate)
            reinv = reinvestment_lst[-1] * reinvestment_rate
            fcff = op_inc - reinv
            future_income_lst.append(op_inc)
            reinvestment_lst.append(reinv)
            fcff_lst.append(fcff)
        self.future_earnings = {
                            "income": future_income_lst,
                            "reinvestment": reinvestment_lst,
                            "fcff": fcff_lst
                            }
    def calc_terminal_value(self, growth_rate, stable_reinv_rate, cost_of_capital):
        terminal_cashflow = self.future_earnings["fcff"][-1]
        terminal_value = terminal_cashflow * (1 + growth_rate) * (1 - stable_reinv_rate) / cost_of_capital - growth_rate
        print(f"terminal value {terminal_value}") # the same for both
        # discounted_terminal_value = (self.future_earnings["fcff"][1] / (1 + cost_of_capital)) + (self.future_earnings["fcff"][2] / (1 + cost_of_capital)) + (self.future_earnings["fcff"][3] / (1 + cost_of_capital)) 
        # + (self.future_earnings["fcff"][4] + terminal_value) / (1 + cost_of_capital)
        discounted_terminal_value = self.__calc_terminal_value(cost_of_capital, terminal_value)
        return discounted_terminal_value
    def __calc_terminal_value(self, cost_of_capital, terminal_value):
        discounted_terminal_value = 0
        for i in range(1, self.years_to_predict - 1):
            print(i)
            discounted_terminal_value += (self.future_earnings["fcff"][i]) / (1 + cost_of_capital)
        discounted_terminal_value += (self.future_earnings["fcff"][4]) + (terminal_value / (1 + cost_of_capital))
        return discounted_terminal_value
    def main(self):
        balance_sheet = stock_info.get_balance_sheet(self.ticker)
        balance_sheet = balance_sheet.dropna(thresh=8, axis=1)
        balance_sheet = balance_sheet.replace(np.nan, 0)
        cash_flow = stock_info.get_cash_flow(self.ticker)
        cash_flow = cash_flow.dropna(thresh=8, axis=1)
        cash_flow = cash_flow.replace(np.nan, 0)
        income_statement = stock_info.get_income_statement(self.ticker)
        income_statement = income_statement.dropna(thresh=8, axis=1)
        income_statement = income_statement.replace(np.nan, 0)
        self.__get_balance_sheet_variables(balance_sheet)
        self.__get_cash_flow_variables(cash_flow)
        self.__get_income_statement_variables(income_statement)
        self.__get_quote_variables()
        self.__get_metrics_variables()
        default_spread = self.calc_default_spread(self.interest)
        cost_of_capital = self.calc_cost_of_capital(default_spread)
        growth_rate = self.calculate_growth_rate()
        print(f"growth_rate{growth_rate}")# og: 0.090849689668371-now:0.090849689668371
        roc = self.net_income / (self.total_assets - self.current_liabilities)
        print(f"roc{roc}")# og: 0.05476562048436506-now:0.05476562048436506
        working_capital = self.calc_working_capital()
        print(f"working_capital{working_capital}") # og: 9915000.0-now:9915000.0
        reinvestment_rate = (abs(self.capex) + working_capital) / self.net_income
        print(f"reinvestment_rate{reinvestment_rate}") # 5.0214599824098505-now:5.0214599824098505
        fcff = self.net_income * (100 - reinvestment_rate)
        reinvestment_rate = reinvestment_rate / 100
        self.pred_future_growth(growth_rate, reinvestment_rate)
        stable_reinv_rate = (growth_rate / roc) / 100# og: 0.016588817740923342 now:0.016588817740923342
        terminal_cashflow = self.future_earnings["fcff"][-1]
        print(f"terminal_cashflow{terminal_cashflow}")# og:8781221.522861168 now: 8781221.522861168
        print(f"stable_reinv_rate{stable_reinv_rate}")# og: 0.016588817740923342 now 0.016588817740923342
        print({f"cost_of_capital {cost_of_capital}"}) # og: 0.09230000000000001 now 0.09230000000000001
        discounted_terminal_value = self.calc_terminal_value(growth_rate, stable_reinv_rate, cost_of_capital)
        print(f"discounted_terminal_value {discounted_terminal_value}")# og 20303749.105937358 # 102059464.78311972
        print("future_earnings") # same as og
        print(self.future_earnings)
        #og: 20303749.105937358 new: 3126581.421904809
        total = discounted_terminal_value + self.cash - (self.short_term_debt + self.long_term_debt)
        print(f"total{total}") #og30349749.105937358 new:13172581.42190481
        value_company = (total - self.minority)/100
        print(f"value_company{value_company}")# og: 403957.4910593736 now:131725.8142190481
        value_per_share = float(value_company)/self.shares
        return value_per_share

ticker = "HOTC.L"
risk_free_rate = 1.25 
equity_risk_premium = 6
tax = 0.2
years_to_predict = 5

t = Wacc(ticker, risk_free_rate, equity_risk_premium, tax, years_to_predict)
t2 = t.main()
print(t2)