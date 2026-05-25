def lookup_symbol(smartApi, stock_name):
    """
    Searches the Angel One symbol master for the given stock name.
    Normalizes the query, deduplicates results, and filters out non-EQ (retail) variants
    unless the user explicitly requests advanced mode by prefixing their query with '*'.
    
    Returns a dictionary containing 'exchange', 'tradingsymbol', and 'symboltoken', or None.
    """
    raw_query = stock_name.strip()
    advanced_mode = False
    
    # Prefixing search query with '*' activates advanced mode to show all instrument variants
    if raw_query.startswith("*"):
        advanced_mode = True
        raw_query = raw_query[1:]
        
    query = raw_query.upper().replace(" ", "")
    
    if not query:
        print("Stock name query cannot be empty.")
        return None
        
    try:
        response = smartApi.searchScrip(exchange="NSE", searchscrip=query)
    except Exception as e:
        print(f"Error during symbol lookup: {e}")
        return None
        
    if not response.get("status") or not response.get("data"):
        print(f"No symbols found matching: '{raw_query}'")
        return None
        
    matches = response["data"]
    
    # Filter matches to ensure they contain the query segment
    filtered_matches = []
    for item in matches:
        symbol = item.get("tradingsymbol", "").upper()
        if query in symbol:
            filtered_matches.append(item)
            
    if not filtered_matches:
        filtered_matches = matches
        
    # Deduplicate results by trading symbol
    seen_symbols = set()
    deduped_matches = []
    for item in filtered_matches:
        sym = item.get("tradingsymbol", "").upper()
        if sym not in seen_symbols:
            seen_symbols.add(sym)
            deduped_matches.append(item)
            
    # Retail Mode: Prioritize and display ONLY standard '-EQ' equity shares.
    # Exclude institutional/settlement variants (-BE, -BL, -AF, -IQ, -RL, etc.)
    if not advanced_mode:
        eq_matches = [item for item in deduped_matches if item.get("tradingsymbol", "").upper().endswith("-EQ")]
        if eq_matches:
            deduped_matches = eq_matches

    # Check for direct exact EQ segment match (e.g. query-EQ) for user convenience
    exact_eq_match = f"{query}-EQ"
    for item in deduped_matches:
        if item.get("tradingsymbol", "").upper() == exact_eq_match:
            return item
            
    # If exactly one match remains, auto-select it directly without asking
    if len(deduped_matches) == 1:
        return deduped_matches[0]
        
    # Multiple matches found - prompt the user to choose from standard listings
    print(f"\nMultiple matches found for '{raw_query}'{' (Advanced Mode)' if advanced_mode else ''}:")
    for i, item in enumerate(deduped_matches, 1):
        print(f"  {i}. {item.get('tradingsymbol')} (Token: {item.get('symboltoken')})")
        
    while True:
        try:
            choice = input(f"Select stock (1-{len(deduped_matches)}) or press Enter to cancel: ").strip()
            if choice == "":
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(deduped_matches):
                return deduped_matches[idx]
            else:
                print(f"Please enter a number between 1 and {len(deduped_matches)}")
        except ValueError:
            print("Invalid input. Please enter a valid number or press Enter to cancel.")

