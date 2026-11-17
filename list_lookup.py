#!/usr/bin/env python3
"""
IP Geolocation Lookup Script using ip-api.com
Processes a list of IP addresses and saves results to CSV
"""

import utils.transport
import utils.session
import csv
import time
import requests
from typing import List, Dict
import sys
import io

def lookup_ip(ip: str, fields: str = None) -> Dict:
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
        print(f"Error looking up {ip}: {e}")
        return {"query": ip, "status": "error", "message": str(e)}

def process_ip_list(ip_list: List[str], output_file: str, fields: str = None):
    """
    Process a list of IP addresses and save results to CSV
    
    Args:
        ip_list: List of IP addresses to process
        output_file: Path to output CSV file
        fields: Comma-separated field names (optional)
    """
    results = []
    total = len(ip_list)
    
    print(f"Processing {total} IP addresses...")
    
    for i, ip in enumerate(ip_list, 1):
        print(f"[{i}/{total}] Looking up {ip}...")
        
        result = lookup_ip(ip.strip(), fields)
        results.append(result)
        
        # Rate limiting - free tier allows 45 requests per minute
        # Sleep for 1.5 seconds between requests to stay under limit
        if i < total:
            time.sleep(1.5)
    
    # Write results to CSV
    if results:
        fieldnames = results[0].keys()
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\nResults saved to {output_file}")
        print(f"Successfully processed {len(results)} IP addresses")
    else:
        print("No results to save")

def read_ips_from_file(filename: str) -> List[str]:
    """
    Read IP addresses from a text file (one per line)
    
    Args:
        filename: Path to file containing IP addresses
    
    Returns:
        List of IP addresses
    """
    try:
        with open(filename, 'r') as f:
            ips = [line.strip() for line in f if line.strip()]
        return ips
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def main():
    """
    Main function - example usage
    """
    # Example 1: Hardcoded list of IPs
    sample_ips = [
        "216.163.197.24",
        "162.201.78.145",
        "66.65.33.206",
        "172.56.67.194",
        "24.74.6.22",
        "216.163.197.24",
        "107.223.198.11",
        "41.56.217.93",
        "24.30.84.129",
        "24.126.151.67",
        "72.94.180.135",
        "129.222.252.80",
        "73.54.175.57",
        "174.220.207.231,"
        "99.155.81.26",
        "107.128.19.154",
        "129.222.252.80",
        "73.7.86.166",
        "99.33.26.140",
        "38.13.186.247",
        "173.188.128.219,"
        "136.55.177.214",
        "108.245.17.4",
        "99.185.127.64",
        "99.35.42.28",
        "178.95.208.6",
        "75.180.208.86",
        "107.223.197.131,"
        "86.62.29.67",
        "172.56.182.244",
        "73.7.225.177",
        "172.59.24.196",
        "216.24.219.216",
        "45.26.8.35",
        "51.159.225.198",
        "24.216.109.33",
        "136.55.172.212",
        "71.131.39.81",
        "172.56.71.15",
        "216.163.197.24"
    ]
    
    # Example 2: Read IPs from file (uncomment to use)
    # sample_ips = read_ips_from_file("ip_list.txt")
    
    # Specify which fields you want (optional)
    # Available fields: status,message,continent,continentCode,country,countryCode,
    # region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,
    # org,as,asname,reverse,mobile,proxy,hosting,query
    
    # Using default common fields
    fields = "status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
    
    # Or use ALL fields (uncomment to use)
    # fields = "status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
    
    # Process IPs and save to CSV
    output_filename = "ip_geolocation_results.csv"
    process_ip_list(sample_ips, output_filename, fields)

if __name__ == "__main__":
    main()