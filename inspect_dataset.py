import pandas as pd

path = r'c:\\Users\\priti\\Desktop\\retail sales\\data\\ecommerce_orders_dataset.csv'

df = pd.read_csv(path)
print('Rows:', len(df))
print('Columns:', list(df.columns))
print('Dtypes:')
print(df.dtypes)
print('Missing values per column:')
print(df.isnull().sum())
print('Duplicate rows:', df.duplicated().sum())
profit_cols = [c for c in df.columns if 'profit' in c.lower()]
print('Profit columns detected:', profit_cols)
if profit_cols:
    col = profit_cols[0]
    print(f'Profit stats for {col}:')
    print(df[col].describe())
