from datetime import datetime, timedelta, timezone

def check_market_status():
    """
    Checks if the Indian Stock Market (NSE/BSE) is currently open.
    Trading hours are Monday to Friday, 09:15 AM to 03:30 PM IST (Indian Standard Time).
    
    Returns:
        is_open (bool): True if open, False if closed.
        status_msg (str): A user-friendly message describing the status.
    """
    # Define IST (Indian Standard Time) as UTC + 5:30
    ist_timezone = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist_timezone)
    
    # Check if weekend (Saturday = 5, Sunday = 6)
    weekday = now_ist.weekday()
    if weekday >= 5:
        day_name = "Saturday" if weekday == 5 else "Sunday"
        return False, f"CLOSED ({day_name})"
        
    # Check market timing: 09:15 to 15:30 IST
    market_start = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
    market_end = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)
    
    if market_start <= now_ist <= market_end:
        return True, "OPEN"
    elif now_ist < market_start:
        return False, f"CLOSED (Before Market Hours. Opens at 09:15 AM IST)"
    else:
        return False, f"CLOSED (After Market Hours. Closed at 03:30 PM IST)"
