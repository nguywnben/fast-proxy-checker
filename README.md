# Fast Proxy Checker

A high-performance, multithreaded Python tool to validate proxies with automatic protocol detection, geolocation lookup, and authentication support.

## Key Features
- **Multithreading:** Blazing fast validation with user-defined thread counts.
- **Smart Protocol Detection:** Automatically tests HTTP, HTTPS, SOCKS4, and SOCKS5 if no protocol is specified.
- **Full Auth Support:** Handles `ip:port:user:pass` and `user:pass@ip:port` formats seamlessly.
- **Real-time Geolocation:** Displays the country and latency (ms) for every live proxy.
- **Clean UI:** Professional color-coded console output (Live in Green, Dead in Red).
- **Format Preservation:** Saves working proxies to `live_proxies.txt` while keeping your original format.
- **Auto-Reset:** Automatically clears the output file at the start of each session.

## Supported Formats
The checker supports all common proxy formats in `proxies.txt`:
- `1.2.3.4:8080` (Auto-detects all protocols)
- `socks5://1.2.3.4:1080` (Explicit protocol)
- `1.2.3.4:8080:user:pass` (Auth support)
- `user:pass@1.2.3.4:8080` (Standard auth format)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/nguywnben/fast-proxy-checker.git
   ```
2. Install the required library:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Populate your list in `proxies.txt`.
2. Run the script:
   ```bash
   python main.py
   ```
3. Enter the number of threads when prompted (Default is 20).
4. Check `live_proxies.txt` for the results.

## Requirements
- Python 3.x
- `requests[socks]`