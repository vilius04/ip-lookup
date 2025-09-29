#!/usr/bin/env python3
"""
Interactive IP Geolocation Lookup Script using ip-api.com
Prompts user for IP addresses and displays results
"""

import csv
import requests
import io
import json
from datetime import datetime

def lookup_ip(ip: str, fields: str = None) -> dict:
    """
    Look up geolocation data for a single IP address
    
    Args:
        ip: IP address to look up
        fields: Comma-separated field names (optional)
    
    Returns:
        Dictionary with IP data or error information
    """
    base_url = "http://ip-api.com/csv/"
    
    # Default fields if none specified
    if fields is None:
        fields = "status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
    
    url = f"{base_url}{ip}?fields={fields}"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        field_list = fields.split(',')
        csv_reader = csv.reader(io.StringIO(response.text.strip()))
        values = next(csv_reader)  # Get the first (and only) row
        
        result = dict(zip(field_list, values))
        
        if 'query' not in result:
            result['query'] = ip
            
        return result
        
    except requests.exceptions.RequestException as e:
        return {"query": ip, "status": "error", "message": str(e)}
    except Exception as e:
        return {"query": ip, "status": "error", "message": str(e)}

def display_result(result: dict):
    """
    Display IP lookup result in a formatted way
    
    Args:
        result: Dictionary containing IP lookup data
    """
    print("\n" + "="*60)
    
    if result.get('status') == 'success':
        print(f"✓ Lookup Successful for {result.get('query', 'Unknown IP')}")
        print("-"*60)
        
        print(f"📍 Location: {result.get('city', 'N/A')}, {result.get('regionName', 'N/A')}, {result.get('country', 'N/A')}")
        print(f"   Country Code: {result.get('countryCode', 'N/A')}")
        print(f"   ZIP/Postal: {result.get('zip', 'N/A')}")
        
        lat = result.get('lat', 'N/A')
        lon = result.get('lon', 'N/A')
        print(f"\n🌐 Coordinates: {lat}, {lon}")
        if lat != 'N/A' and lon != 'N/A':
            print(f"   Google Maps: https://maps.google.com/?q={lat},{lon}")
        
        print(f"\n🕐 Timezone: {result.get('timezone', 'N/A')}")
        
        print(f"\n🌍 Network Information:")
        print(f"   ISP: {result.get('isp', 'N/A')}")
        print(f"   Organization: {result.get('org', 'N/A')}")
        print(f"   AS: {result.get('as', 'N/A')}")
        
    elif result.get('status') == 'fail':
        print(f"✗ Lookup Failed for {result.get('query', 'Unknown IP')}")
        print(f"   Error: {result.get('message', 'Unknown error')}")
    else:
        print(f"✗ Error occurred for {result.get('query', 'Unknown IP')}")
        print(f"   Error: {result.get('message', 'Unknown error')}")
    
    print("="*60)

def save_to_csv(results: list, filename: str = None):
    """
    Save results to a CSV file
    
    Args:
        results: List of lookup results
        filename: Output filename (optional, will be auto-generated if not provided)
    """
    if not results:
        print("No results to save")
        return
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ip_lookups_{timestamp}.csv"
    
    fieldnames = []
    for result in results:
        for key in result.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n💾 Results saved to {filename}")

def main():
    """
    Main interactive loop
    """
    print("="*60)
    print("      Interactive IP Geolocation Lookup Tool")
    print("           Using ip-api.com (Free Tier)")
    print("="*60)
    print("\nCommands:")
    print("  - Enter an IP address to look it up")
    print("  - Type 'save' to save all results to CSV")
    print("  - Type 'clear' to clear result history")
    print("  - Type 'help' to show commands")
    print("  - Type 'quit' or 'exit' to exit")
    print("\nNote: Free tier limited to 45 requests per minute")
    print("="*60)
    
    results = []
    request_count = 0
    
    while True:
        try:
            user_input = input("\n🔍 Enter IP address (or command): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! 👋")
                if results:
                    save_prompt = input("Save results before exiting? (y/n): ").strip().lower()
                    if save_prompt == 'y':
                        save_to_csv(results)
                break
            
            elif user_input.lower() == 'save':
                if results:
                    save_to_csv(results)
                else:
                    print("No results to save yet")
            
            elif user_input.lower() == 'clear':
                results = []
                request_count = 0
                print("✓ Result history cleared")
            
            elif user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("  IP address - Look up geolocation for the IP")
                print("  save       - Save all results to CSV file")
                print("  clear      - Clear result history")
                print("  help       - Show this help message")
                print("  quit/exit  - Exit the program")
            
            elif user_input == '':
                continue
            
            else:
                print(f"\nLooking up {user_input}...")
                
                result = lookup_ip(user_input)
                
                display_result(result)
                
                result['lookup_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                results.append(result)
                request_count += 1
                
                print(f"\n📊 Total lookups this session: {request_count}")
                
                if request_count % 40 == 0:
                    print("\n⚠️  Approaching rate limit (45 requests/minute)")
                    print("    Consider waiting a moment before continuing")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            if results:
                save_prompt = input("Save results before exiting? (y/n): ").strip().lower()
                if save_prompt == 'y':
                    save_to_csv(results)
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again")

if __name__ == "__main__":
    main()