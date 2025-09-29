# IP Geolocation Lookup Tool

A Python-based CLI tool for looking up geolocation information for IP addresses using the [ip-api.com](http://ip-api.com) free API.

## Features

- 🔍 **Single IP Lookup** - Interactive mode for looking up individual IP addresses
- 📁 **Batch Processing** - Process multiple IPs from CSV or TXT files
- 📊 **CSV Export** - Automatically save results to timestamped CSV files
- 🌍 **Detailed Information** - Get location, ISP, timezone, coordinates, and more
- ⚡ **Rate Limiting** - Built-in rate limiting to comply with free tier limits (45 requests/min)
- 🔄 **Multiple Encoding Support** - Handles CSV files with various encodings

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ip-lookup.git
cd ip-lookup
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests
```

## Usage

### Quick Start

Run the main script:
```bash
python lookup.py
```

### Main Menu Options

When you run the script, you'll see a menu with three options:

```
1. Single IP Lookup
2. Batch Lookup from File (TXT/CSV)
3. Exit
```

### Option 1: Single IP Lookup

Enter IP addresses one at a time to get detailed geolocation information:

```
🔍 Enter IP address (or command): 8.8.8.8
```

**Available Commands:**
- Enter any IP address to look it up
- Type `save` to export all results to CSV
- Type `back` to return to main menu

**Example Output:**
```
============================================================
✓ Lookup Successful for 8.8.8.8
------------------------------------------------------------
📍 Location: Mountain View, California, United States
   Country Code: US
   ZIP/Postal: 94035

🌐 Coordinates: 37.386, -122.0838
   Google Maps: https://maps.google.com/?q=37.386,-122.0838

🕐 Timezone: America/Los_Angeles

🌍 Network Information:
   ISP: Google LLC
   Organization: Google Public DNS
   AS: AS15169 Google LLC
============================================================
```

### Option 2: Batch Lookup from File

Process multiple IP addresses from a file at once.

#### Supported File Formats

**TXT Files** - One IP address per line:
```
8.8.8.8
1.1.1.1
208.67.222.222
```

**CSV Files** - IPs in any column (you'll be prompted to specify which):
```csv
IP Address,Location,Notes
8.8.8.8,Primary,DNS Server
1.1.1.1,Secondary,Cloudflare
```

#### How to Use Batch Mode

1. Select option `2` from the main menu
2. Enter the full path to your file:
   ```
   📁 Enter file path (or 'back' to return): C:\Users\YourName\Documents\ip_list.txt
   ```
3. For CSV files, specify which column contains the IP addresses
4. Confirm to start processing
5. Results are automatically saved to a timestamped CSV file

#### Example Batch Output

```
[1/3] Looking up 8.8.8.8... ✓ Mountain View, United States
[2/3] Looking up 1.1.1.1... ✓ Sydney, Australia
[3/3] Looking up 208.67.222.222... ✓ San Francisco, United States

============================================================
✓ Completed! Processed 3 IP address(es)
============================================================

💾 Results saved to ip_batch_results_20250929_143022.csv

📊 Summary:
   Successful: 3
   Failed: 0
```

## Output CSV Format

All exported CSV files contain the following columns (in order):

| Column | Description |
|--------|-------------|
| status | Success, fail, or error |
| message | Error message (if applicable) |
| country | Country name |
| countryCode | Two-letter country code |
| region | Region/state code |
| regionName | Region/state name |
| city | City name |
| zip | ZIP/postal code |
| lat | Latitude |
| lon | Longitude |
| timezone | Timezone |
| isp | Internet Service Provider |
| org | Organization |
| as | Autonomous System info |
| query | The IP address that was looked up |
| lookup_time | Timestamp of the lookup |

## API Rate Limits

This tool uses the free tier of ip-api.com which has the following limits:

- **45 requests per minute**
- Non-commercial use only

The script automatically implements rate limiting (1.5 seconds between requests) to stay within these limits.

## Legacy Scripts

The repository also includes two standalone scripts for specific use cases:

- `single_lookup.py` - Original single IP lookup script
- `list_lookup.py` - Original batch processing script with hardcoded IP list

These are maintained for backward compatibility but we recommend using `lookup.py` for the best experience.

## Troubleshooting

### Module Not Found Error

If you get `ModuleNotFoundError: No module named 'requests'`:
```bash
python -m pip install requests
```

### CSV Encoding Issues

The script automatically handles multiple encodings (UTF-8, Latin-1, Windows-1252, etc.). If you still have issues, try re-saving your CSV file in UTF-8 encoding.

### File Path Issues

- On Windows, use full paths: `C:\Users\YourName\Documents\file.csv`
- You can include or omit quotes around the path
- Paths with spaces are supported

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool is for educational and non-commercial use only. Please respect ip-api.com's terms of service and rate limits.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

Made with ❤️ for network administrators, security researchers, and curious developers.