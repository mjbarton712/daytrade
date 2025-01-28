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
        tickers: List[str], # List of stock tickers to monitor
        lookback_period: int = 30, # 30-day moving average to look over for mean reversion
        deviation_threshold: float = 0.07, # 7% deviation from moving average to trigger alert
    ):
        """
        Initialize Mean Reversion Alert Bot with Discord notifications
        """
        # Load environment variables
        load_dotenv()
        
        # Discord webhook URL
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        
        self.tickers = tickers
        self.lookback_period = lookback_period
        self.deviation_threshold = deviation_threshold
        
        # Logging setup
        self.log_file = "mean_reversion_alerts.log"

    def _send_discord_alert(self, message: str):
        """
        Send Discord alert
        """
        try:
            payload = {
                "content": message,
                "username": "Trading Alert Bot"
            }
            
            response = requests.post(
                self.discord_webhook_url,
                json=payload
            )
            
            if response.status_code == 204:  # Discord returns 204 on success
                self._log(f"Discord notification sent: {message}")
            else:
                self._log(f"Failed to send Discord notification: {response.text}")
                
        except Exception as e:
            self._log(f"Error sending Discord notification: {e}")

    # [Previous _fetch_historical_data and _log methods remain the same]
    def _fetch_historical_data(self, ticker: str) -> pd.DataFrame:
        try:
            stock_data = yf.download(ticker, period=f"{self.lookback_period}d")
            return stock_data
        except Exception as e:
            self._log(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()

    def _log(self, message: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {message}\n"
        print(log_entry.strip())
        with open(self.log_file, "a") as log:
            log.write(log_entry)

    def calculate_mean_reversion_signals(self) -> dict:
        signals = {}
        
        for ticker in self.tickers:
            data = self._fetch_historical_data(ticker)
            
            if data.empty:
                continue
            
            data["MA"] = data["Close"].rolling(window=self.lookback_period).mean()
            current_price = data["Close"].iloc[-1]
            current_ma = data["MA"].iloc[-1]
            pct_deviation = (current_price - current_ma) / current_ma
            
            if abs(pct_deviation) >= self.deviation_threshold:
                signal_type = "SHORT" if pct_deviation >= self.deviation_threshold else "LONG"
                signals[ticker] = {
                    "signal": signal_type,
                    "current_price": current_price,
                    "moving_average": current_ma,
                    "percent_deviation": pct_deviation * 100,
                }
                
                alert_message = (
                    f"🚨 MEAN REVERSION ALERT: {ticker}\n"
                    f"Signal: {signal_type}\n"
                    f"Current Price: ${current_price:.2f}\n"
                    f"Moving Average: ${current_ma:.2f}\n"
                    f"Deviation: {pct_deviation * 100:.2f}%"
                )
                self._log(alert_message)
                self._send_discord_alert(alert_message)
        
        return signals

    def run_alert_bot(self, interval: int = 10): # Scan every 10 seconds for mean reversion signals
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

def main():
    tickers = ["AAPL", "GOOGL", "MSFT", "AMZN"]  # Replace with your watchlist
    
    bot = MeanReversionAlertBot(
        tickers=tickers,
        lookback_period=30,
        deviation_threshold=0.07
    )
    
    bot.run_alert_bot()

if __name__ == "__main__":
    main()

# Setup Instructions:
"""
DISCORD SETUP GUIDE:

1. Create a Discord server (if you don't have one):
   - Open Discord
   - Click the + button on the left sidebar
   - Choose "Create My Own"
   - Follow the setup steps

2. Create a webhook:
   - Right-click the channel you want to receive alerts in
   - Select "Edit Channel"
   - Click "Integrations"
   - Click "Create Webhook"
   - Click "Copy Webhook URL"

3. Environment Setup:
   - Create a .env file in your project directory
   - Add: DISCORD_WEBHOOK_URL=your_webhook_url_here

4. Dependencies:
   pip install yfinance python-dotenv requests pandas numpy

5. Run the bot:
   python your_script_name.py
"""