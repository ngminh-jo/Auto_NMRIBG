```python

df = pd.DataFrame()
df["ten_column"] = list()
row_mask = list()
for name in df["ten_column"]:
    if "machine_bau"  in name:
        row_mask.append(True)
    else:
        row_mask.append(False)
df_true = df.loc[row_mask]
df_false = df.loc[[- i for i in row_mask]]
```
