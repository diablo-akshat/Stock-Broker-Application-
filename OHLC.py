import http.client
import json

conn = http.client.HTTPSConnection("apiconnect.angelone.in")

payload = json.dumps({
    "mode": "OHLC",
    "exchangeTokens": {
        "NSE": ["1333"]
    }
}).encode("utf-8")

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-UserType': 'USER',
    'X-SourceID': 'WEB',
    'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJ1c2VybmFtZSI6Ikc1MjAyMTUyNSIsInJvbGVzIjowLCJ1c2VydHlwZSI6IlVTRVIiLCJ0b2tlbiI6ImV5SmhiR2NpT2lKU1V6STFOaUlzSW5SNWNDSTZJa3BYVkNKOS5leUoxYzJWeVgzUjVjR1VpT2lKamJHbGxiblFpTENKMGIydGxibDkwZVhCbElqb2lkSEpoWkdWZllXTmpaWE56WDNSdmEyVnVJaXdpWjIxZmFXUWlPakV5TENKemIzVnlZMlVpT2lJeklpd2laR1YyYVdObFgybGtJam9pTlRJd05XWTBaVEl0WkdNME1DMHpZMkppTFdJMU9ETXROakpqWW1Jd01EWmxNamMwSWl3aWEybGtJam9pZEhKaFpHVmZhMlY1WDNZeElpd2liMjF1WlcxaGJtRm5aWEpwWkNJNk1USXNJbkJ5YjJSMVkzUnpJanA3SW1SbGJXRjBJanA3SW5OMFlYUjFjeUk2SW1GamRHbDJaU0o5TENKdFppSTZleUp6ZEdGMGRYTWlPaUpoWTNScGRtVWlmWDBzSW1semN5STZJblJ5WVdSbFgyeHZaMmx1WDNObGNuWnBZMlVpTENKemRXSWlPaUpITlRJd01qRTFNalVpTENKbGVIQWlPakUzTXpneU1qWXhNVFlzSW01aVppSTZNVGN6T0RFek9UVXpOaXdpYVdGMElqb3hOek00TVRNNU5UTTJMQ0pxZEdraU9pSTRPVE5qTW1NME55MW1NalV4TFRSa1pUSXRZbUk1T0MxbE4yVXpNakJrWmpoaU5HUWlMQ0pVYjJ0bGJpSTZJaUo5Lm5XVEJWS2d0V3RZa0RtZ3pTT1Z4S210V3ZXdWRUdjBfcHJZRlV6MFJqaUJ2RU1JZ0dTWkswZDI1ZHVwLU90c1FZYXo4bkdUdDJOUVpybXFZdXFwWHlsaWQtVmRxSFdzaG9qakpUZURYT3V4MktJUG9GcWdBcFJVcFcxTHFQSUU3dXJfRFo1MUx3VUxTOEZsb2xOVmxVYy1RVnpTOUlYQ3VTODZUak9WYWNONCIsIkFQSS1LRVkiOiJnVlRRWGtvRyIsImlhdCI6MTczODEzOTcxNiwiZXhwIjoxNzM4MjI2MTE2fQ.qIQvqKn7Ac8wr4XeB9ZoxKhT1e8tDkGv6PuKJwajg-Ma7E6HP9udxUqWChddIWqhsZNZmX5SwVrSx8pwALUoSQ',
    'X-ClientLocalIP': '192.168.1.13',
    'X-ClientPublicIP': '223.185.133.146',
    'X-MACAddress': 'B6-8C-9D-52-B7-AB',
    'X-PrivateKey': 'gVTQXkoG'
}

conn.request("POST", "/rest/secure/angelbroking/market/v1/quote/", payload, headers)

res = conn.getresponse()
data = res.read()

try:
    response_dict = json.loads(data.decode("utf-8"))  # Print full response

    if "status" in response_dict:
        if response_dict["status"]:
            fetched_data = response_dict["data"]["fetched"][0]
            print(f"{fetched_data['tradingSymbol']}")
            print(f"LTP: {fetched_data['ltp']}")
            print(f"Open: {fetched_data['open']}")
            print(f"High: {fetched_data['high']}")
            print(f"Low: {fetched_data['low']}")
            print(f"Close: {fetched_data['close']}")
        else:
            print("API returned an error:", response_dict.get("message", "Unknown error"))
    else:
        print("Unexpected response format: 'status' key not found!")

except json.JSONDecodeError:
    print("Failed to decode JSON. Raw response:", data.decode("utf-8"))
