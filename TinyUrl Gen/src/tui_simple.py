import os
import sys
import time
from typing import Optional
import msvcrt

from src.logger import Logger
from src.proxy_manager import ProxyManager
from src.url_classifier import URLClassifier
from src.tinyurl_generator import TinyURLGenerator
from src.link_checker import LinkChecker
from src.models import ProxyConfig
from src.config import Config


class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


class SimpleTUI:
    def __init__(self):
        self.config = Config()
        
        self.total = 0
        self.uhq = 0
        self.hq = 0
        self.bad = 0
        self.not_found = 0
        
        self.menu_items = [
            ("Generate URLs", "g"),
            ("Configure Settings", "c"),
            ("Show Statistics", "s"),
            ("Quit", "q")
        ]
        self.selected = 0
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{' ' * 25}TinyURL Generator & Checker{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}")
    
    def print_config(self):
        print(f"\n{Colors.BOLD}{Colors.YELLOW}[Configuration]{Colors.RESET}")
        print(f"{Colors.GREEN}  Pattern:{Colors.RESET} {self.config.pattern}")
        print(f"{Colors.GREEN}  Count:{Colors.RESET} {self.config.count}")
        print(f"{Colors.GREEN}  Log File:{Colors.RESET} {self.config.log_file}")
        print(f"{Colors.GREEN}  Proxy File:{Colors.RESET} {self.config.proxy_file if self.config.proxy_file else f'{Colors.DIM}(none){Colors.RESET}'}")
    
    def print_stats(self):
        print(f"\n{Colors.BOLD}{Colors.YELLOW}[Statistics]{Colors.RESET}")
        print(f"{Colors.CYAN}  Total Generated:{Colors.RESET} {self.total}")
        print(f"{Colors.RED}  Not Found:{Colors.RESET} {self.not_found}")
        print(f"{Colors.GREEN}  UHQ URLs:{Colors.RESET} {self.uhq}")
        print(f"{Colors.BLUE}  HQ URLs:{Colors.RESET} {self.hq}")
        print(f"{Colors.DIM}  BAD URLs:{Colors.RESET} {self.bad}")
    
    def print_menu(self):
        print(f"\n{Colors.BOLD}{Colors.YELLOW}[Actions]{Colors.RESET}")
        print(f"{Colors.DIM}Use ↑↓ arrows to navigate, Enter to select{Colors.RESET}\n")
        
        for idx, (label, key) in enumerate(self.menu_items):
            if idx == self.selected:
                print(f"{Colors.BG_CYAN}{Colors.BLACK}  → {label} {Colors.RESET}")
            else:
                print(f"    {label}")
    
    def get_key(self):
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\xe0':
                key = msvcrt.getch()
                if key == b'H':
                    return 'UP'
                elif key == b'P':
                    return 'DOWN'
            elif key == b'\r':
                return 'ENTER'
            elif key == b'q':
                return 'q'
            elif key == b'g':
                return 'g'
            elif key == b'c':
                return 'c'
            elif key == b's':
                return 's'
        return None
    
    def configure(self):
        self.clear_screen()
        self.print_header()
        print(f"\n{Colors.BOLD}{Colors.YELLOW}[Configure Settings]{Colors.RESET}")
        print(f"{Colors.DIM}Press Enter to keep current value{Colors.RESET}\n")
        
        new_pattern = input(f"{Colors.GREEN}Pattern{Colors.RESET} [{self.config.pattern}]: ").strip()
        if new_pattern:
            self.config.pattern = new_pattern
        
        new_count = input(f"{Colors.GREEN}Count{Colors.RESET} [{self.config.count}]: ").strip()
        if new_count:
            try:
                self.config.count = int(new_count)
            except ValueError:
                print(f"{Colors.RED}Invalid count, keeping current value{Colors.RESET}")
                time.sleep(1)
        
        new_log = input(f"{Colors.GREEN}Log File{Colors.RESET} [{self.config.log_file}]: ").strip()
        if new_log:
            self.config.log_file = new_log
        
        new_proxy_file = input(f"{Colors.GREEN}Proxy File{Colors.RESET} [{self.config.proxy_file if self.config.proxy_file else 'none'}]: ").strip()
        if new_proxy_file:
            self.config.proxy_file = new_proxy_file
        
        print(f"\n{Colors.GREEN}Configuration saved to config.json!{Colors.RESET}")
        time.sleep(1)
    
    def generate(self):
        self.clear_screen()
        self.print_header()
        print(f"\n{Colors.BOLD}{Colors.YELLOW}[Generating URLs...]{Colors.RESET}\n")
        
        self.total = 0
        self.uhq = 0
        self.hq = 0
        self.bad = 0
        self.not_found = 0
        
        try:
            logger = Logger(self.config.log_file)
            
            proxy_file_path = self.config.proxy_file if self.config.proxy_file else None
            
            if proxy_file_path:
                print(f"{Colors.CYAN}Loading and testing proxies from: {proxy_file_path}{Colors.RESET}")
            
            proxy_manager = ProxyManager(None, proxy_file_path, self.config.test_proxies)
            
            if proxy_file_path and proxy_manager.proxy_list:
                print(f"{Colors.GREEN}Loaded {len(proxy_manager.proxy_list)} working proxies{Colors.RESET}\n")
            
            
            classifier = URLClassifier()
            generator = TinyURLGenerator(logger)
            checker = LinkChecker(proxy_manager, logger)
            
            print(f"{Colors.YELLOW}Generating {self.config.count} URLs with pattern: {self.config.pattern}{Colors.RESET}\n")
            
            candidates = generator.generate_candidates(self.config.pattern, self.config.count)
            self.total = len(candidates)
            
            print(f"{Colors.GREEN}Generated {len(candidates)} candidates{Colors.RESET}\n")
            print(f"{Colors.YELLOW}Validating and checking redirects...{Colors.RESET}\n")
            
            for idx, url in enumerate(candidates, 1):
                print(f"{Colors.DIM}[{idx}/{len(candidates)}]{Colors.RESET} Checking: {Colors.CYAN}{url}{Colors.RESET}")
                
                exists = checker.check_existence(url)
                
                if not exists:
                    self.not_found += 1
                    print(f"  {Colors.RED}✗ Not found{Colors.RESET}")
                    continue
                
                destination = checker.get_redirect_destination(url)
                
                if destination:
                    tier = classifier.classify(destination)
                    logger.log_classification(destination, tier)
                    
                    if tier == "UHQ":
                        self.uhq += 1
                        print(f"  {Colors.BOLD}{Colors.GREEN}✓ UHQ{Colors.RESET} → {destination}")
                    elif tier == "HQ":
                        self.hq += 1
                        print(f"  {Colors.BOLD}{Colors.BLUE}✓ HQ{Colors.RESET} → {destination}")
                    else:
                        self.bad += 1
                        print(f"  {Colors.DIM}✓ BAD{Colors.RESET} → {destination}")
                else:
                    self.not_found += 1
            
            print(f"\n{Colors.BOLD}{Colors.GREEN}{'=' * 80}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.GREEN}Generation Complete!{Colors.RESET}")
            self.print_stats()
            print(f"\n{Colors.CYAN}Log saved to: {self.config.log_file}{Colors.RESET}")
            print(f"{Colors.CYAN}UHQ URLs saved to: logs/uhq.txt{Colors.RESET}")
            print(f"{Colors.CYAN}HQ URLs saved to: logs/hq.txt{Colors.RESET}")
            print(f"{Colors.CYAN}BAD URLs saved to: logs/bad.txt{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 80}{Colors.RESET}")
            
        except ValueError as e:
            print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
        except FileNotFoundError as e:
            print(f"\n{Colors.RED}File error: {e}{Colors.RESET}")
        except Exception as e:
            print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        
        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
    
    def show_stats(self):
        self.clear_screen()
        self.print_header()
        self.print_stats()
        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
    
    def run(self):
        while True:
            self.clear_screen()
            self.print_header()
            self.print_config()
            self.print_stats()
            self.print_menu()
            
            while True:
                key = self.get_key()
                if key:
                    break
                time.sleep(0.05)
            
            if key == 'UP':
                self.selected = (self.selected - 1) % len(self.menu_items)
            elif key == 'DOWN':
                self.selected = (self.selected + 1) % len(self.menu_items)
            elif key == 'ENTER':
                action = self.menu_items[self.selected][1]
                if action == 'g':
                    self.generate()
                elif action == 'c':
                    self.configure()
                elif action == 's':
                    self.show_stats()
                elif action == 'q':
                    print(f"\n{Colors.CYAN}Goodbye!{Colors.RESET}")
                    sys.exit(0)
            elif key == 'g':
                self.generate()
            elif key == 'c':
                self.configure()
            elif key == 's':
                self.show_stats()
            elif key == 'q':
                print(f"\n{Colors.CYAN}Goodbye!{Colors.RESET}")
                sys.exit(0)


def main():
    os.system('')
    tui = SimpleTUI()
    tui.run()


if __name__ == "__main__":
    main()
