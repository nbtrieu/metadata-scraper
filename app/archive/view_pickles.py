import pickle
import pandas as pd

leads_keywords_df = pd.read_pickle('./outputs/leads_keywords_1.pkl')
print("FROM PICKLE:\n", leads_keywords_df)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
print(leads_keywords_df)
