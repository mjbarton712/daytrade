# daytrade

## General
This repo is meant to explore a mean reversion trading daytrade technique.

Mean reversion trading is a financial strategy that assumes that asset prices will revert to their historical average or mean over time. The basic idea is that if the price of an asset deviates significantly from its historical average, it will eventually return to that average. Traders using this strategy will buy assets that are undervalued (below their mean) and sell assets that are overvalued (above their mean), expecting that prices will revert to the mean.

Key points of this technique:
- Historical Average: The mean or average price over a specific period.
- Deviation: The difference between the current price and the historical average.
- Reversion: The expectation that prices will move back towards the mean.

This strategy relies on statistical analysis and historical data to identify potential trading opportunities. 

There are a number of variables that can be changed such as tickers to watch, percentage different than average, and more - explore the daytrade.py file to see more info.

## How to create a python virtual env with a requirements.txt in general:
This is mainly for me so I have a reference for future projects lol.
- Create virtual env: `python -m venv venv`
- Activate virtual env: `venv\Scripts\activate` (for Mac/Linux, `source venv/bin/activate`)
- Install deps in virtual env: `pip install your-libraries`
- Update requirements.txt with virtual env deps: `pip freeze > requirements.txt`
- Deactivate virtual env: `deactivate`

If you want to use this project and have a virtual env to be clean and not have global installs:
- Clone the repository
- Create and activate a virtual environment as above
- Install the dependencies: `pip install -r requirements.txt`

## Environment variables?
Of course - here is a list of what you will need to run this!

```Conf
PUSHBULLET_API_TOKEN=your_pushbullet_api_token```