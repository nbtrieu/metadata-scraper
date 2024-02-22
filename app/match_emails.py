import pandas as pd

df = pd.read_csv("data/trimmed_ucla_emails_hunter.csv")

df['hunter_email_normalized'] = df['email'].str.lower()
df['original_email_normalized'] = df['original_email'].str.lower()

df['is_match'] = df['hunter_email_normalized'] == df['original_email_normalized']

matches_percentage = (df['is_match'].sum() / len(df)) * 100

print(f"Percentage of matches: {matches_percentage}%")
