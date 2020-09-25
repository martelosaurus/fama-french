# fama_french
Implements a Python class for downloading, cleaning, and plotting Fama French factors from Ken French's website 

```python
FF = FamaFrench()
FF.plot_annual(start=1980) # plots value of a dollar invested in 1980
df = FF.get_monthly() # returns a Pandas DataFrame with monthly returns
df.head()
```

