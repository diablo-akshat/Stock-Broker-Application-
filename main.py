import sys
import pandas as pd
from datetime import datetime, timedelta
from auth import login_and_setup
from symbol_lookup import lookup_symbol
from market_status import check_market_status
from live_data import handle_live_data
from config import apikey, username

def display_menu():
    print("\n" + "=" * 35)
    print("      Angel One Stock Market Tool")
    print("=" * 35)
    print("1. Live Streaming (Real-Time)")
    print("2. Refresh Every Minute")
    print("3. Historical OHLC Data")
    print("4. Exit")
    print("=" * 35)

def main():
    print("Initializing system and logging in...")
    try:
        smartApi = login_and_setup()
    except Exception as e:
        print(f"\nCRITICAL: Authentication failed: {e}")
        print("Please check your credentials in config.py and ensure your TOTP secret is correct.")
        sys.exit(1)

    while True:
        display_menu()
        choice = input("Enter your choice (1-4): ").strip()

        if choice == "4":
            print("\nThank you for using Angel One Stock Market Tool. Goodbye!")
            sys.exit(0)
            
        if choice not in ["1", "2", "3"]:
            print("Invalid choice. Please enter a number between 1 and 4.")
            continue

        # Stock Lookup Stage
        stock_query = input("\nEnter stock name (e.g. HDFCBANK, RELIANCE): ").strip()
        if not stock_query:
            print("Stock name cannot be empty.")
            continue

        print(f"Searching symbol master for '{stock_query}'...")
        resolved_stock = lookup_symbol(smartApi, stock_query)
        
        if resolved_stock is None:
            print("Stock resolution failed. Returning to menu.")
            continue

        symboltoken = resolved_stock["symboltoken"]
        tradingsymbol = resolved_stock["tradingsymbol"]
        print(f"Resolved stock: {tradingsymbol} (Token: {symboltoken})")

        # Action Stage
        if choice in ["1", "2"]:
            # Live Market Mode (Real-Time vs Polling)
            is_open, status_msg = check_market_status()
            
            # Extract tokens required by WebSocket (Real-Time Mode)
            access_token = smartApi.access_token
            bearer_token = f"Bearer {access_token}" if not access_token.startswith("Bearer ") else access_token
            feed_token = smartApi.getfeedToken()
            
            mode_param = "REALTIME" if choice == "1" else "POLLING"
            
            handle_live_data(
                smartApi=smartApi,
                auth_token=bearer_token,
                api_key=apikey,
                username=username,
                feed_token=feed_token,
                symboltoken=symboltoken,
                tradingsymbol=tradingsymbol,
                is_open=is_open,
                status_msg=status_msg,
                mode=mode_param
            )
        elif choice == "3":
            # Historical OHLC Mode - Last 30 calendar days
            try:
                todate = datetime.now()
                fromdate = todate - timedelta(days=30)
                
                historicDataParams = {
                    "exchange": "NSE",
                    "symboltoken": symboltoken,
                    "interval": "ONE_DAY",
                    "fromdate": fromdate.strftime("%Y-%m-%d %H:%M"),
                    "todate": todate.strftime("%Y-%m-%d %H:%M")
                }
                print(f"\n--- Fetching last 30 calendar days OHLC (params: {historicDataParams}) ---")
                response = smartApi.getCandleData(historicDataParams)
                
                if response.get("status") and "data" in response and response["data"] is not None:
                    candle_data = response["data"]
                    df = pd.DataFrame(candle_data, columns=["Timestamp", "Open", "High", "Low", "Close", "Volume"])
                    # Format timestamp strings to show dates cleanly (e.g. YYYY-MM-DD)
                    df['Timestamp'] = df['Timestamp'].apply(lambda x: x.split('T')[0] if 'T' in str(x) else str(x))
                    df = df.iloc[::-1].reset_index(drop=True)
                    print(df)
                else:
                    print(f"Error fetching historical data: {response.get('message', 'Unknown Historical Data Error')} (Code: {response.get('errorCode', 'None')})")
            except Exception as e:
                print(f"Exception during historical data fetching: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Exiting cleanly.")
        sys.exit(0)