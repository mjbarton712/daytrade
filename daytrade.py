import yfinance as yf
import numpy as np
import pandas as pd
import time
import os
from typing import List
import requests
from dotenv import load_dotenv


class MeanReversionAlertBot:
    def __init__(
        self,
        tickers: List[str], # List of stock ticker symbols to monitor
        lookback_period: int = 30, # 30-day moving average
        deviation_threshold: float = 0.07, # 7% deviation threshold
    ):
        """
        Initialize Mean Reversion Alert Bot with SMS and logging capabilities

        :param tickers: List of stock ticker symbols to monitor
        :param lookback_period: Number of days to calculate moving average
        :param deviation_threshold: Percentage threshold for mean reversion alert
        """
        # Load environment variables
        load_dotenv()

        # Twilio credentials for SMS (free alternatives will be discussed)
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from_number = os.getenv("TWILIO_FROM_NUMBER")
        self.your_phone_number = os.getenv("YOUR_PHONE_NUMBER")

        self.tickers = tickers
        self.lookback_period = lookback_period
        self.deviation_threshold = deviation_threshold

        # Logging setup
        self.log_file = "mean_reversion_alerts.log"

    def _fetch_historical_data(self, ticker: str) -> pd.DataFrame:
        """
        Fetch historical stock data for a given ticker

        :param ticker: Stock ticker symbol
        :return: Pandas DataFrame with historical price data
        """
        try:
            stock_data = yf.download(ticker, period=f"{self.lookback_period}d")
            return stock_data
        except Exception as e:
            self._log(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()

    def _send_sms(self, message: str):
        """
        Send SMS alert (Twilio method)

        :param message: Alert message to send
        """
        try:
            # Twilio SMS sending (commented out for free alternatives explanation)
            # url = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json".format(self.twilio_account_sid)
            # auth = (self.twilio_account_sid, self.twilio_auth_token)
            # data = {
            #     "From": self.twilio_from_number,
            #     "To": self.your_phone_number,
            #     "Body": message
            # }
            # response = requests.post(url, data=data, auth=auth)

            # Free Alternative: Pushbullet Notification
            pushbullet_token = os.getenv("PUSHBULLET_API_TOKEN")
            if pushbullet_token:
                headers = {
                    "Access-Token": pushbullet_token,
                    "Content-Type": "application/json",
                }
                payload = {
                    "type": "note",
                    "body": message,
                    "title": "Mean Reversion Alert",
                }
                response = requests.post(
                    "https://api.pushbullet.com/v2/pushes",
                    headers=headers,
                    json=payload,
                )
                if response.status_code == 200:
                    self._log(f"Notification sent: {message}")
                else:
                    self._log(f"Failed to send notification: {response.text}")
            else:
                print("No notification method configured.")

        except Exception as e:
            self._log(f"Error sending notification: {e}")

    def _log(self, message: str):
        """
        Log messages to file and print to console

        :param message: Message to log
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {message}\n"

        print(log_entry.strip())

        with open(self.log_file, "a") as log:
            log.write(log_entry)

    def calculate_mean_reversion_signals(self) -> dict:
        """
        Calculate mean reversion signals for all tracked tickers

        :return: Dictionary of trading signals
        """
        signals = {}

        for ticker in self.tickers:
            data = self._fetch_historical_data(ticker)

            if data.empty:
                continue

            # Calculate moving average
            data["MA"] = data["Close"].rolling(window=self.lookback_period).mean()

            # Current price
            current_price = data["Close"].iloc[-1]
            current_ma = data["MA"].iloc[-1]

            # Calculate percentage deviation
            pct_deviation = (current_price - current_ma) / current_ma

            # Determine trading signal
            if abs(pct_deviation) >= self.deviation_threshold:
                signal_type = (
                    "SHORT" if pct_deviation >= self.deviation_threshold else "LONG"
                )
                signals[ticker] = {
                    "signal": signal_type,
                    "current_price": current_price,
                    "moving_average": current_ma,
                    "percent_deviation": pct_deviation * 100,
                }

                # Prepare and send alert
                alert_message = (
                    f"MEAN REVERSION ALERT: {ticker}\n"
                    f"Signal: {signal_type}\n"
                    f"Current Price: ${current_price:.2f}\n"
                    f"Moving Average: ${current_ma:.2f}\n"
                    f"Deviation: {pct_deviation * 100:.2f}%"
                )
                self._log(alert_message)
                self._send_sms(alert_message)

        return signals

    def run_alert_bot(self, interval: int = 10):
        """
        Continuously run the alert bot

        :param interval: Check interval in seconds (default 10 seconds)
        """
        self._log("Mean Reversion Alert Bot Started...")

        while True:
            try:
                self.calculate_mean_reversion_signals()
                time.sleep(interval)

            except KeyboardInterrupt:
                self._log("\nBot stopped by user.")
                break
            except Exception as e:
                self._log(f"An error occurred: {e}")
                time.sleep(interval)


# Deployment Instructions
def main():
    # Example tickers - replace with your own watch list
    tickers = ["AAPL", "GOOGL", "MSFT", "AMZN"]

    # Initialize and run the bot
    bot = MeanReversionAlertBot(
        tickers=tickers,
        lookback_period=30,  # 30-day moving average
        deviation_threshold=0.07,  # 7% deviation threshold
    )

    bot.run_alert_bot()


if __name__ == "__main__":
    main()

# README for 24/7 Deployment

"""
DEPLOYMENT GUIDE:

1. Free 24/7 Hosting Options:
   - Heroku (Free Tier)
   - PythonAnywhere (Free Tier)
   - Google Cloud Run (Free Tier)
   - AWS Lambda with CloudWatch (Free Tier)

2. Notification Methods (Free):
   a) Pushbullet (Recommended)
      - Create a free account at pushbullet.com
      - Get API token
      - Install pushbullet app on phone
   
   b) Alternative Free Notification Options:
      - Telegram Bot
      - Discord Webhooks
      - Email-to-SMS services

3. Required Environment Variables (.env file):
   PUSHBULLET_API_TOKEN=your_pushbullet_token
   -OR-
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_FROM_NUMBER=your_twilio_from_number
   YOUR_PHONE_NUMBER=your_phone_number
   
4. Dependencies:
   pip install yfinance python-dotenv requests pandas numpy

5. Deployment Considerations:
   - Use process managers like Supervisor for reliability
   - Implement error handling and restart mechanisms
   - Consider API rate limits
   - Add logging for troubleshooting
"""
