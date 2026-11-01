"""
This script tracks and displays the current stock prices for a list of specified ticker symbols.
It uses the `yfinance` library to fetch real-time (or near real-time) stock data from Yahoo Finance.
The script can periodically update prices, providing a simple stock price tracker.
"""

# pip install yfinance

import yfinance as yf
import time
from datetime import datetime

def get_stock_price(ticker_symbol: str) -> float | None:
    """
    Fetches the current regular market price for a given stock ticker symbol.

    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., "AAPL", "MSFT").

    Returns:
        float | None: The current regular market price of the stock, or None if
                      the price cannot be fetched (e.g., invalid ticker, network issue).
    """
    try:
        # Create a Ticker object for the given symbol
        stock = yf.Ticker(ticker_symbol)
        
        # Fetch the most recent information about the stock.
        # The .info dictionary contains a lot of data, including various pricing points.
        data = stock.info
        
        # 'regularMarketPrice' is generally the current price during market hours.
        # 'currentPrice' might include pre/post-market, depending on context and availability.
        # We prioritize 'regularMarketPrice' for a standard "current price" tracker.
        price = data.get('regularMarketPrice')
        
        if price is not None:
            return float(price)
        else:
            # If regularMarketPrice isn't available, try currentPrice as a fallback.
            price = data.get('currentPrice')
            if price is not None:
                return float(price)
            else:
                print(f"Warning: Could not find a current price for {ticker_symbol}.")
                return None
                
    except Exception as e:
        # Catch any exceptions that might occur during data fetching
        # (e.g., invalid ticker symbol, network error, API issue).
        print(f"Error fetching price for {ticker_symbol}: {e}")
        return None

def track_stocks(tickers: list[str], interval_seconds: int = 10, num_updates: int = 5):
    """
    Tracks and displays the stock prices for a list of tickers over time.

    Args:
        tickers (list[str]): A list of stock ticker symbols to track.
        interval_seconds (int): The time interval (in seconds) between price updates.
                                Defaults to 10 seconds.
        num_updates (int): The number of times to update and display the prices.
                           Set to -1 for continuous tracking until manually stopped (Ctrl+C).
                           Defaults to 5 updates.
    """
    print(f"\n--- Starting Stock Price Tracker ---")
    print(f"Tracking: {', '.join(tickers)}")
    print(f"Updates every {interval_seconds} seconds. Total updates: {num_updates if num_updates != -1 else 'continuous'}\n")

    update_count = 0
    try:
        while num_updates == -1 or update_count < num_updates:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Update {update_count + 1} at {current_time}:")
            
            for ticker in tickers:
                price = get_stock_price(ticker)
                if price is not None:
                    # Print the ticker and its price, formatted to 2 decimal places and left-aligned.
                    print(f"  {ticker:<8}: ${price:,.2f}") 
                else:
                    print(f"  {ticker:<8}: Price not available.")
            
            update_count += 1
            
            # Only pause if there are more updates to come or if tracking continuously.
            if num_updates == -1 or update_count < num_updates:
                print(f"Next update in {interval_seconds} seconds...\n")
                time.sleep(interval_seconds)
            else:
                print("\n--- Tracking finished. ---")

    except KeyboardInterrupt:
        # Allow the user to stop continuous tracking gracefully with Ctrl+C.
        print("\n--- Tracking interrupted by user. Exiting. ---")
    except Exception as e:
        print(f"\nAn unexpected error occurred during tracking: {e}")

if __name__ == "__main__":
    # --- Example Usage ---
    
    # 1. Define a list of stock ticker symbols you want to track.
    #    You can add or remove tickers as needed.
    #    Ensure the tickers are valid (e.g., "AAPL" for Apple, "MSFT" for Microsoft).
    my_tickers = ["AAPL", "MSFT", "GOOG", "TSLA", "AMZN", "NVDA", "IBM"]

    # 2. Start tracking these stocks.
    #    This example fetches prices every 7 seconds for 4 updates.
    print("--- Running example: Tracking multiple stocks for a few updates ---")
    track_stocks(my_tickers, interval_seconds=7, num_updates=4)

    # 3. You can also fetch a single price instantly outside of the tracking loop.
    print("\n--- Running example: Fetching a single price instantly ---")
    single_ticker_to_check = "AMD"
    amd_price = get_stock_price(single_ticker_to_check)
    if amd_price is not None:
        print(f"Current price for {single_ticker_to_check}: ${amd_price:,.2f}")
    else:
        print(f"Failed to get price for {single_ticker_to_check}.")

    # 4. Example of continuous tracking (uncomment to run)
    #    This will fetch prices every 15 seconds until you press Ctrl+C to stop it.
    # print("\n--- Running example: Continuous tracking (press Ctrl+C to stop) ---")
    # track_stocks(["NFLX", "SBUX"], interval_seconds=15, num_updates=-1)
