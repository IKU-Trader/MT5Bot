import pandas as pd
import numpy as np
import sklearn.mixture as mix
from pandas_datareader.data import DataReader
import matplotlib.pyplot as plt
import yfinance as yf

# Machine Learning
from hmmlearn.hmm import GaussianHMM

# Data Extraction
start_date = "2017-01-1"
end_date = "2023-07-01"
symbol = "SPY"
data = yf.download(symbol, start=start_date, end=end_date)
data = data[["Open", "High", "Low", "Close", "Volume"]]
data.head(3)

df = data.copy()
df["Log"] = np.log(df["Close"])
df["Returns"] = df["Log"].pct_change()
df["Range"] = (df["High"] / df["Low"]) - 1
df.dropna(inplace=True)
df.head()



n = len(df)
m = int(n * 0.5)


df_train = df.iloc[:m, :]
df_test = df.iloc[m:, :]

X_train =  df_train[["Returns", "Range"]]
X_test = df_test[["Returns", "Range"]]


X_train.head()

# Fit Model
# INITIAL VIDEO SHOWED GMM (above) - BUT HMM SEEMS BETTER?
while True:
    try:
        hmm_model = GaussianHMM(n_components=4, covariance_type="full", n_iter=100).fit(X_train)
        print("Model Score:", hmm_model.score(X_train))
        break
    except:
        continue


# Check results
hidden_states = hmm_model.predict(X_test)
hidden_states[:5]

i = 0
labels_0 = []
labels_1 = []
labels_2 = []
labels_3 = []
prices = df_test["Close"].values.astype(float)
print("Correct Number of rows: ", len(prices) == len(hidden_states))
for s in hidden_states:
    if s == 0:
        labels_0.append(prices[i])
        labels_1.append(float('nan'))
        labels_2.append(float('nan'))
        labels_3.append(float('nan'))
    if s == 1:
        labels_0.append(float('nan'))
        labels_1.append(prices[i])
        labels_2.append(float('nan'))
        labels_3.append(float('nan'))
    if s == 2:
        labels_0.append(float('nan'))
        labels_1.append(float('nan'))
        labels_2.append(prices[i])
        labels_3.append(float('nan'))
    if s == 3:
        labels_0.append(float('nan'))
        labels_1.append(float('nan'))
        labels_2.append(float('nan'))
        labels_3.append(prices[i])
    i += 1
    
    
# Plot chart
fig = plt.figure(figsize = (18,10))
plt.plot(labels_0, color="red")
plt.plot(labels_1, color="green")
plt.plot(labels_2, color="black")
plt.plot(labels_3, color="orange")
plt.show()
print(len(labels_0))


# Create the class
class StrategyManager():

    # Initialize the class
    def __init__(self, symbol, start_date, end_date):
        self.df = self._extract_data(symbol, start_date, end_date)
        self.sharpe = 0

    # Extract data
    def _extract_data(self, symbol, start_date, end_date):
        import yfinance as yf
        data = yf.download(symbol, start=start_date, end=end_date)
        data = data[["Open", "High", "Low", "Close", "Volume"]]
        data = self._structure_df(data)
        return data

    # Calculates general period returns and volatility
    def _structure_df(self, df):
        df["Returns"] = df["Close"].pct_change()
        df["Range"] = df["High"] / df["Low"] - 1
        df["Bench_C_Rets"], sharpe = self._calculate_returns(df, True)
        self.sharpe = sharpe
        df.dropna(inplace=True)
        return df

    # Adjusts the signal to represent our strategy
    def _set_multiplier(self, direction):
        if direction == "long":
            pos_multiplier = 1
            neg_multiplier = 0
        elif direction == "long_short":
            pos_multiplier = 1
            neg_multiplier = -1
        else:
            pos_multiplier = 0
            neg_multiplier = -1
        return pos_multiplier, neg_multiplier

    # Calculates returns for equity curve
    def _calculate_returns(self, df, is_benchmark):

        # Calculate multiplier
        if not is_benchmark:
            multiplier_1 = df["Signal"].shift(1)
            multiplier_2 = 1 if "PSignal" not in df.columns else df["PSignal"].shift(1)

            # Assume open price on following day to avoid lookahead bias for close calculation
            log_rets = np.log(df["Open"].shift(-1) / df["Open"]) * multiplier_1 * multiplier_2
        else:
            log_rets = np.log(df["Close"] / df["Close"].shift(1))

        # Calculate Sharpe Ratio
        sharpe_ratio = self.sharpe_ratio(log_rets)

        # Calculate Cumulative Returns
        c_log_rets = log_rets.cumsum()
        c_log_rets_exp = np.exp(c_log_rets) - 1

        # Return result and Sharpe ratio
        return c_log_rets_exp, sharpe_ratio

    def sharpe_ratio(self, return_series):
        N = 255 # Trading days in the year (change to 365 for crypto)
        rf = 0.005 # Half a percent risk free rare
        mean = return_series.mean() * N -rf
        sigma = return_series.std() * np.sqrt(N)
        sharpe = round(mean / sigma, 3)
        return sharpe

    # Replace Dataframe
    def change_df(self, new_df, drop_cols=[]):
        new_df = new_df.drop(columns=drop_cols)
        self.df = new_df

    # Moving average crossover strategy
    def backtest_ma_crossover(self, period_1, period_2, direction, drop_cols=[]):

        # Set df
        df = self.df

        # Get multipliers
        pos_multiplier, neg_multiplier = self._set_multiplier(direction)

        # Calculate Moving Averages
        if f"MA_{period_1}" or f"MA_{period_2}" not in df.columns:
            df[f"MA_{period_1}"] = df["Close"].rolling(window=period_1).mean()
            df[f"MA_{period_2}"] = df["Close"].rolling(window=period_2).mean()
            df.dropna(inplace=True)

        # Calculate Benchmark Returns
        df["Bench_C_Rets"], sharpe_ratio_bench = self._calculate_returns(df, True)

        # Calculate Signal
        df.loc[df[f"MA_{period_1}"] > df[f"MA_{period_2}"], "Signal"] = pos_multiplier
        df.loc[df[f"MA_{period_1}"] <= df[f"MA_{period_2}"], "Signal"] = neg_multiplier

        # Calculate Strategy Returns
        df["Strat_C_Rets"], sharpe_ratio_strat = self._calculate_returns(df, False)

        # Get values for output
        bench_rets = df["Bench_C_Rets"].values.astype(float)
        strat_rets = df["Strat_C_Rets"].values.astype(float)
        print("Sense check: ", round(df["Close"].values[-1] / df["Close"].values[0] - 1, 3), round(bench_rets[-1], 3))

        # Remove irrelevant features
        if len(drop_cols) > 0:
            df = df.drop(columns=drop_cols)

        # Ensure Latest DF matches
        df = df.dropna()
        self.df = df

        # Return df
        return df, sharpe_ratio_bench, sharpe_ratio_strat
    
# Create an instance
strat_mgr = StrategyManager(symbol, start_date, end_date)

# Extract the modified data
df_strat_mgr = strat_mgr.df
df_strat_mgr.tail()

# Check MA Strategy performance
strat_df, sharpe_b, sharpe_s = strat_mgr.backtest_ma_crossover(12, 21, "long", drop_cols=["High", "Low", "Volume"])
strat_df

# Review equity curve and metrics
print("Sharpe Ratio Base Strategy Benchmark: ", sharpe_b)
print("Sharpe Ratio Base Strategy: ", sharpe_s)

fig = plt.figure(figsize = (18,10))
plt.plot(strat_df["Bench_C_Rets"])
plt.plot(strat_df["Strat_C_Rets"])
plt.show()

# Structure Data
X_train_2 = strat_df[["Returns", "Range"]].iloc[:500] # Train Test Split here
X_test = strat_df[["Returns", "Range"]].iloc[500:]
X_train_2.head()
df_strat_mgr_test = strat_df.copy()
len(X_train_2)

# Fit Model
while True:
    try:
        hmm_model = GaussianHMM(n_components=4, covariance_type="full", n_iter=100).fit(X_train_2)
        print("Model Score:", hmm_model.score(X_train_2))
        break
    except:
        continue


# Predict Market Regimes
hidden_states_preds = hmm_model.predict(X_test.values)
hidden_states_preds[:10]
len(hidden_states_preds)

# Set Favourable States - !!!!!!!!! ADJUST BASED ON HMM RESULTS AND TEST OUTCOME !!!!!!!!!!!!!!!!!!!!
favourable_states = [1, 2]

# Write Strategy
state_signals = []
for s in hidden_states_preds:
    if s in favourable_states:
        state_signals.append(1)
    else:
        state_signals.append(0)
print("States: ", state_signals[:10])
print("Lengh of States: ", len(state_signals))


# Replace Strategy Dataframe
df_strat_mgr_test = df_strat_mgr_test.tail(len(X_test))
df_strat_mgr_test["PSignal"] = state_signals
strat_mgr.change_df(df_strat_mgr_test)
strat_mgr.df.head()

strat_df_2, sharpe_b_2, sharpe_s_2 = strat_mgr.backtest_ma_crossover(12, 21, "long")
strat_df_2

# Review equity curve
print("Sharpe Ratio Benchmark: ", sharpe_b_2)
print("Sharpe Ratio Regime Strategy with MA Cross: ", sharpe_s_2)
print("--- ---")
print(f"Returns Benchmark: {round(strat_df_2['Bench_C_Rets'].values[-1] * 100, 2)}%")
print(f"Returns Regime Strategy with MA Cross: {round(strat_df_2['Strat_C_Rets'].values[-1] * 100, 2)}%")

fig = plt.figure(figsize = (18, 10))
plt.plot(strat_df_2["Bench_C_Rets"])
plt.plot(strat_df_2["Strat_C_Rets"])
plt.show()

