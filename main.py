import requests
import time
import threading
import sys
from concurrent.futures import ThreadPoolExecutor

class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

class ProxyChecker:
    def __init__(self, input_file="proxies.txt"):
        self.input_file = input_file
        self.proxies = self.load_proxies()
        self.total = len(self.proxies)
        self.counter = 0
        self.live_count = 0
        self.dead_count = 0
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.clear_output_file()

    def clear_output_file(self):
        with open("valid_proxies.txt", "w") as f:
            f.write("")

    def load_proxies(self):
        try:
            with open(self.input_file, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return []

    def get_location(self, ip):
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("country", "Unknown")
        except:
            return "Unknown"
        return "Unknown"

    def parse_proxy(self, raw_proxy):
        protocol = None
        if '://' in raw_proxy:
            protocol, raw_proxy = raw_proxy.split('://', 1)
        
        ip = port = user = passw = None
        
        if '@' in raw_proxy:
            auth, host = raw_proxy.split('@', 1)
            auth_parts = auth.split(':')
            if len(auth_parts) == 2:
                user, passw = auth_parts
            host_parts = host.split(':')
            if len(host_parts) == 2:
                ip, port = host_parts
        else:
            parts = raw_proxy.split(':')
            if len(parts) == 4:
                ip, port, user, passw = parts
            elif len(parts) == 2:
                ip, port = parts
                
        if not ip or not port:
            return None, None, None
            
        if user and passw:
            base_addr = f"{user}:{passw}@{ip}:{port}"
        else:
            base_addr = f"{ip}:{port}"
            
        return protocol, base_addr, ip

    def check_single_proxy(self, proxy_address):
        if self.stop_event.is_set():
            return

        protocol, base_addr, pure_ip = self.parse_proxy(proxy_address)
        
        if not base_addr:
            with self.lock:
                self.counter += 1
                self.dead_count += 1
                print(f"[{self.counter}/{self.total}] {Color.RED}Dead{Color.RESET} | {proxy_address} (Invalid Format)")
            return

        if protocol:
            protocols_to_test = [protocol]
        else:
            protocols_to_test = ['http', 'https', 'socks5', 'socks4']
        
        found_valid = False
        display_info = ""
        file_info = ""
        
        original_no_proto = proxy_address.split('://')[-1]

        for p in protocols_to_test:
            if self.stop_event.is_set(): 
                break
            
            req_url = f"{p}://{base_addr}"
            save_url = f"{p}://{original_no_proto}"
            
            try:
                start_time = time.time()
                proxies = {"http": req_url, "https": req_url}
                response = requests.get("http://www.google.com", proxies=proxies, timeout=5)
                
                if response.status_code == 200:
                    latency = round((time.time() - start_time) * 1000)
                    country = self.get_location(pure_ip)
                    display_info = f"{save_url} -> {Color.YELLOW}{country} ({latency}ms){Color.RESET}"
                    file_info = save_url
                    found_valid = True
                    break
            except:
                continue

        with self.lock:
            if self.stop_event.is_set() and not found_valid:
                return
                
            self.counter += 1
            if found_valid:
                self.live_count += 1
                print(f"[{self.counter}/{self.total}] {Color.GREEN}Live{Color.RESET} | {display_info}")
                with open("valid_proxies.txt", "a") as f:
                    f.write(file_info + "\n")
                    f.flush()
            else:
                self.dead_count += 1
                print(f"[{self.counter}/{self.total}] {Color.RED}Dead{Color.RESET} | {proxy_address}")

    def run(self, threads=15):
        if not self.proxies:
            print("No proxies found in proxies.txt.")
            return

        print(f"Started running with {self.total} proxies.")
        print("-" * 60)
        print()
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            try:
                futures = [executor.submit(self.check_single_proxy, p) for p in self.proxies]
                while any(f.running() for f in futures):
                    time.sleep(0.5)
            except KeyboardInterrupt:
                self.stop_event.set()
                print(f"\n{Color.RED}Process stopped. Canceling remaining tasks...{Color.RESET}")
                executor.shutdown(wait=False)
        
        print()
        print("-" * 60)
        print(f"Check completed. Total: {self.total} | Live: {self.live_count} | Dead: {self.dead_count}")

if __name__ == "__main__":
    checker = ProxyChecker("proxies.txt")
    
    try:
        user_input = input("Enter number of threads (Default: 20): ").strip()
        num_threads = int(user_input) if user_input else 20
        if num_threads <= 0:
            print(f"{Color.RED}Invalid number. Using default 20 threads.{Color.RESET}")
            num_threads = 20
    except ValueError:
        print(f"{Color.RED}Invalid input. Using default 20 threads.{Color.RESET}")
        num_threads = 20
        
    print()
    checker.run(threads=num_threads)