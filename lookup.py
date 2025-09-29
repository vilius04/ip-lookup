#!/usr/bin/env python3
"""
IP Geolocation Lookup Tool with Menu
Allows single IP lookup or batch processing from CSV/TXT files
"""

import csv
import requests
import io
import time
import sys
import os
from datetime import datetime
from typing import List, Dict

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
        values = next(csv_reader)
        
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

def read_ips_from_txt(filename: str) -> List[str]:
    """
    Read IP addresses from a text file (one per line)
    
    Args:
        filename: Path to TXT file containing IP addresses
    
    Returns:
        List of IP addresses
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            ips = [line.strip() for line in f if line.strip()]
        return ips
    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found")
        return None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def read_ips_from_csv(filename: str, ip_column: str = None) -> List[str]:
    """
    Read IP addresses from a CSV file
    
    Args:
        filename: Path to CSV file containing IP addresses
        ip_column: Name of column containing IPs (will prompt if not provided)
    
    Returns:
        List of IP addresses
    """
    # Try different encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                raw_fieldnames = reader.fieldnames
                
                if not raw_fieldnames:
                    print("❌ Error: CSV file appears to be empty or invalid")
                    return None
                
                # Clean fieldnames - remove BOM and extra whitespace
                fieldnames = [field.strip().lstrip('\ufeff').strip() for field in raw_fieldnames]
                
                # Create mapping from clean names to original names
                name_mapping = dict(zip(fieldnames, raw_fieldnames))
                
                # If no column specified, show available columns and ask user
                if ip_column is None:
                    print(f"\nAvailable columns in CSV: {', '.join(fieldnames)}")
                    ip_column = input("Enter the column name containing IP addresses: ").strip()
                
                # Find the original column name
                original_column = name_mapping.get(ip_column)
                
                if original_column is None:
                    print(f"❌ Error: Column '{ip_column}' not found in CSV")
                    print(f"Available columns: {', '.join(fieldnames)}")
                    return None
                
                # Reset file pointer and read IPs
                f.seek(0)
                reader = csv.DictReader(f)
                ips = [row[original_column].strip() for row in reader if row.get(original_column, '').strip()]
                
                return ips
        
        except UnicodeDecodeError:
            # Try next encoding
            continue
        except FileNotFoundError:
            print(f"❌ Error: File '{filename}' not found")
            return None
        except Exception as e:
            print(f"❌ Error reading CSV file: {e}")
            return None
    
    # If all encodings failed
    print(f"❌ Error: Unable to read CSV file with supported encodings")
    print(f"   Tried: {', '.join(encodings)}")
    return None

def save_to_csv(results: List[dict], filename: str = None):
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
    
    # Define the correct column order
    fieldnames = [
        'status', 'message', 'country', 'countryCode', 'region', 'regionName', 
        'city', 'zip', 'lat', 'lon', 'timezone', 'isp', 'org', 'as', 'query', 
        'lookup_time'
    ]
    
    # Only include columns that exist in the results
    existing_fieldnames = []
    for field in fieldnames:
        if any(field in result for result in results):
            existing_fieldnames.append(field)
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=existing_fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\n💾 Results saved to {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error saving to CSV: {e}")
        return None

def single_ip_mode():
    """
    Interactive mode for single IP lookups
    """
    print("\n" + "="*60)
    print("         Single IP Lookup Mode")
    print("="*60)
    print("\nCommands:")
    print("  - Enter an IP address to look it up")
    print("  - Type 'save' to save all results to CSV")
    print("  - Type 'back' to return to main menu")
    print("="*60)
    
    results = []
    
    while True:
        try:
            user_input = input("\n🔍 Enter IP address (or command): ").strip()
            
            if user_input.lower() in ['back', 'menu']:
                if results:
                    save_prompt = input("\nSave results before returning to menu? (y/n): ").strip().lower()
                    if save_prompt == 'y':
                        save_to_csv(results)
                break
            
            elif user_input.lower() == 'save':
                if results:
                    save_to_csv(results)
                else:
                    print("No results to save yet")
            
            elif user_input == '':
                continue
            
            else:
                print(f"\nLooking up {user_input}...")
                result = lookup_ip(user_input)
                display_result(result)
                
                result['lookup_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                results.append(result)
                
                print(f"\n📊 Total lookups this session: {len(results)}")
        
        except KeyboardInterrupt:
            print("\n\nReturning to main menu...")
            if results:
                save_prompt = input("Save results before returning? (y/n): ").strip().lower()
                if save_prompt == 'y':
                    save_to_csv(results)
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}")

def batch_lookup_mode():
    """
    Batch lookup mode - process IPs from a file
    """
    print("\n" + "="*60)
    print("         Batch IP Lookup Mode")
    print("="*60)
    print("\nSupported file formats:")
    print("  - TXT files: One IP address per line")
    print("  - CSV files: IPs in a column (you'll specify which)")
    print("="*60)
    
    while True:
        file_path = input("\n📁 Enter file path (or 'back' to return): ").strip()
        
        if file_path.lower() in ['back', 'menu']:
            return
        
        if file_path == '':
            continue
        
        # Remove quotes if user wrapped the path in quotes
        file_path = file_path.strip('"').strip("'")
        
        if not os.path.exists(file_path):
            print(f"❌ Error: File not found at '{file_path}'")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                return
            continue
        
        # Determine file type
        file_ext = os.path.splitext(file_path)[1].lower()
        
        ips = None
        if file_ext == '.txt':
            print(f"\n📄 Reading IPs from TXT file...")
            ips = read_ips_from_txt(file_path)
        
        elif file_ext == '.csv':
            print(f"\n📄 Reading IPs from CSV file...")
            ips = read_ips_from_csv(file_path)
        
        else:
            print(f"⚠️  Unrecognized file extension '{file_ext}'")
            print("Attempting to read as TXT file (one IP per line)...")
            ips = read_ips_from_txt(file_path)
        
        if ips is None:
            retry = input("\nTry another file? (y/n): ").strip().lower()
            if retry != 'y':
                return
            continue
        
        if len(ips) == 0:
            print("❌ No IP addresses found in file")
            retry = input("Try another file? (y/n): ").strip().lower()
            if retry != 'y':
                return
            continue
        
        print(f"\n✓ Found {len(ips)} IP address(es)")
        print(f"⚠️  Note: Free tier allows 45 requests per minute")
        print(f"   Estimated time: ~{int(len(ips) * 1.5 / 60)} minute(s) {int(len(ips) * 1.5 % 60)} seconds")
        
        confirm = input("\nProceed with lookup? (y/n): ").strip().lower()
        if confirm != 'y':
            return
        
        # Process IPs
        results = []
        print(f"\n{'='*60}")
        print("Processing IP addresses...")
        print(f"{'='*60}\n")
        
        for i, ip in enumerate(ips, 1):
            print(f"[{i}/{len(ips)}] Looking up {ip}...", end=" ")
            
            result = lookup_ip(ip)
            result['lookup_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            results.append(result)
            
            if result.get('status') == 'success':
                print(f"✓ {result.get('city', 'N/A')}, {result.get('country', 'N/A')}")
            elif result.get('status') == 'fail':
                print(f"✗ Failed: {result.get('message', 'Unknown error')}")
            else:
                print(f"✗ Error: {result.get('message', 'Unknown error')}")
            
            # Rate limiting - 1.5 seconds between requests
            if i < len(ips):
                time.sleep(1.5)
        
        print(f"\n{'='*60}")
        print(f"✓ Completed! Processed {len(results)} IP address(es)")
        print(f"{'='*60}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"ip_batch_results_{timestamp}.csv"
        
        saved_file = save_to_csv(results, output_filename)
        
        if saved_file:
            print(f"\n📊 Summary:")
            successful = sum(1 for r in results if r.get('status') == 'success')
            failed = len(results) - successful
            print(f"   Successful: {successful}")
            print(f"   Failed: {failed}")
        
        # Ask if user wants to process another file
        another = input("\n\nProcess another file? (y/n): ").strip().lower()
        if another != 'y':
            break

def main():
    """
    Main menu
    """
    print("="*60)
    print("      IP Geolocation Lookup Tool")
    print("           Using ip-api.com")
    print("="*60)
    print("\nFree tier: 45 requests per minute")
    print("="*60)
    
    while True:
        print("\n" + "="*60)
        print("Main Menu:")
        print("="*60)
        print("1. Single IP Lookup")
        print("2. Batch Lookup from File (TXT/CSV)")
        print("3. Exit")
        print("="*60)
        
        try:
            choice = input("\nSelect an option (1-3): ").strip()
            
            if choice == '1':
                single_ip_mode()
            
            elif choice == '2':
                batch_lookup_mode()
            
            elif choice == '3':
                print("\nGoodbye! 👋")
                sys.exit(0)
            
            else:
                print("❌ Invalid option. Please choose 1, 2, or 3")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            sys.exit(0)
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again")

if __name__ == "__main__":
    main()