import lightgbm as lgb
import dill as pickle
import pandas as pd 
import numpy as np 


def train_model(X, y, filename='predictive'):
    params = {
        'objective': 'regression',
        'metric': 'mse',  # Mean Squared Error
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'learning_rate': 0.05,
        'feature_fraction': 0.9,
        'seed': 42
    }

    reg = lgb.LGBMRegressor(**params)
    reg.fit(X, y)

    with open(f'{filename}.pkl', 'wb') as handle:
        pickle.dump(reg, handle, protocol=pickle.HIGHEST_PROTOCOL, recurse=True)

    print(f'New model saved at: {filename}.pkl')


def predict(model, X):
    pred = model.predict(X)
    return pred

def predict_next_30_days(model):
    start_date = pd.to_datetime('today').normalize()
    end_date = start_date + pd.DateOffset(days=30)

    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    df_next = pd.DataFrame(date_range)
    df_next['year'] = df_next[0].dt.year
    df_next['month'] = df_next[0].dt.month
    df_next['day'] = df_next[0].dt.day

    df_next['cos_year'] = np.cos(2 * np.pi * df_next['year'] / 2024)
    df_next['sin_year'] = np.sin(2 * np.pi * df_next['year'] / 2024)

    df_next['cos_month'] = np.cos(2 * np.pi * df_next['month'] / 12)
    df_next['sin_month'] = np.sin(2 * np.pi * df_next['month'] / 12)

    df_next['cos_day'] = np.cos(2 * np.pi * df_next['day'] / 31)
    df_next['sin_day'] = np.sin(2 * np.pi * df_next['day'] / 31)
    columns = ['cos_year', 'sin_year', 'cos_month', 'sin_month', 'cos_day', 'sin_day']
    pred = model.predict(df_next[columns])
    return pred