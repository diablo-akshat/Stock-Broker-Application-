import time
import threading
from datetime import datetime
from smartWebSocketV2 import SmartWebSocketV2
from logzero import logger

def handle_live_data(smartApi, auth_token, api_key, username, feed_token, symboltoken, tradingsymbol, is_open, status_msg, mode="REALTIME"):
    """
    Handles price monitoring. Supporting:
    1. REALTIME: WebSocket tick-by-tick streaming
    2. POLLING: Once every 60 seconds SmartAPI REST polling
    
    If the market is closed, automatically prints the last close quote and exits cleanly.
    """
    if not is_open:
        print("\n-------------------------------------------")
        print(f"Market Status: {status_msg}")
        print("NSE market is currently closed.")
        print("-------------------------------------------")
        
        try:
            # Query getMarketData to fetch the closing price
            response = smartApi.getMarketData(mode="OHLC", exchangeTokens={"NSE": [f"{symboltoken}"]})
            if response.get("status") and response.get("data") and response["data"].get("fetched"):
                fetched_data = response["data"]["fetched"][0]
                close_price = fetched_data.get("close", fetched_data.get("ltp", 0.0))
                print(f"Stock: {tradingsymbol}")
                print(f"Last trading close: Rs. {close_price:.2f}")
            else:
                print(f"Unable to fetch closing price for {tradingsymbol}.")
        except Exception as e:
            print(f"Error retrieving closing price: {e}")
        print("-------------------------------------------")
        input("\nPress Enter to return to menu...")
        return

    # If market is OPEN:
    if mode == "POLLING":
        # Mode 2: 1-Minute Refresh Polling
        print("\n-------------------------------------------")
        print(f"Market Status: {status_msg}")
        print(f"Monitoring {tradingsymbol} (1-Minute Refresh Polling)...")
        print("Press Enter at any time to stop monitoring and return to menu.")
        print("-------------------------------------------")

        stop_event = threading.Event()
        
        def wait_for_user_exit():
            input()
            stop_event.set()
            
        exit_thread = threading.Thread(target=wait_for_user_exit)
        exit_thread.daemon = True
        exit_thread.start()

        while not stop_event.is_set():
            try:
                response = smartApi.getMarketData(mode="OHLC", exchangeTokens={"NSE": [f"{symboltoken}"]})
                if response.get("status") and response.get("data") and response["data"].get("fetched"):
                    fetched_data = response["data"]["fetched"][0]
                    ltp = fetched_data.get("ltp", 0.0)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] {tradingsymbol} Rs. {ltp:.2f}")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Unable to fetch LTP.")
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {e}")
                
            # Sleep in small chunks of 0.5s to respond immediately if the user presses Enter
            for _ in range(120):
                if stop_event.is_set():
                    break
                time.sleep(0.5)
                
        print("\nStopping 1-Minute monitor...")
        return

    # Mode 1: Real-Time Streaming (WebSocket)
    print("\n-------------------------------------------")
    print(f"Market Status: {status_msg}")
    print(f"Streaming live price updates for {tradingsymbol} (Real-Time ticks)...")
    print("Press Enter at any time to stop streaming and return to menu.")
    print("-------------------------------------------")
    
    # Try fetching initial LTP first
    try:
        response = smartApi.getMarketData(mode="OHLC", exchangeTokens={"NSE": [f"{symboltoken}"]})
        if response.get("status") and response.get("data") and response["data"].get("fetched"):
            fetched_data = response["data"]["fetched"][0]
            print(f"Initial LTP: Rs. {fetched_data.get('ltp', 0.0):.2f}\n")
    except Exception as e:
        print(f"Error fetching initial LTP: {e}")

    correlation_id = "live_stream"
    sub_mode = 1  # LTP subscription mode
    token_list = [{"exchangeType": 1, "tokens": [f"{symboltoken}"]}]
    
    sws = SmartWebSocketV2(auth_token, api_key, username, feed_token)
    
    def on_data(wsapp, message):
        try:
            last_traded_price = message.get('last_traded_price', 'N/A')
            timestamp = datetime.now().strftime("%H:%M:%S")
            if isinstance(last_traded_price, (int, float)):
                # Print live tick on separate lines with timestamp
                print(f"[{timestamp}] {tradingsymbol} Live LTP: Rs. {last_traded_price:.2f}")
            else:
                print(f"[{timestamp}] {tradingsymbol} Live LTP: {last_traded_price}")
        except Exception as e:
            logger.error(f"Error processing websocket message: {e}")
            
    def on_open(wsapp):
        try:
            sws.subscribe(correlation_id, sub_mode, token_list)
        except Exception as e:
            logger.error(f"Failed to subscribe to live data: {e}")
        
    def on_error(wsapp, error):
        pass
        
    def on_close(wsapp):
        pass
        
    sws.on_open = on_open
    sws.on_data = on_data
    sws.on_error = on_error
    sws.on_close = on_close
    
    # Start WebSocket connection in a daemon background thread
    ws_thread = threading.Thread(target=sws.connect)
    ws_thread.daemon = True
    ws_thread.start()
    
    # Wait for user input (pressing Enter) to terminate stream
    input()
    
    print("\nStopping live price stream...")
    try:
        sws.close_connection()
    except Exception as e:
        logger.error(f"Error closing WebSocket connection: {e}")
