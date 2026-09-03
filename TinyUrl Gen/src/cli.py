import argparse
import sys
from pathlib import Path
from typing import Optional
from src.logger import Logger
from src.proxy_manager import ProxyManager
from src.url_classifier import URLClassifier
from src.tinyurl_generator import TinyURLGenerator
from src.link_checker import LinkChecker
from src.models import ProxyConfig
from src.config import Config


def parse_arguments():
    parser = argparse.ArgumentParser(description="TinyURL Generator and Checker")
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--pattern",
        type=str,
        default=None,
        help="Regex pattern for TinyURL generation (overrides config)"
    )
    
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Number of TinyURL candidates to generate (overrides config)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Path to log file (overrides config)"
    )
    
    parser.add_argument(
        "--proxy-file",
        type=str,
        default=None,
        help="Path to proxy list file (overrides config)"
    )
    
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip URL validation and redirect checking"
    )
    
    return parser.parse_args()


def main():
    args = parse_arguments()
    
    config = Config(args.config)
    
    pattern = args.pattern if args.pattern else config.pattern
    count = args.count if args.count else config.count
    log_file = args.log_file if args.log_file else config.log_file
    proxy_file = args.proxy_file if args.proxy_file else config.proxy_file
    
    logger = Logger(log_file)
    
    try:
        proxy_manager = ProxyManager(None, proxy_file, config.test_proxies)
        
        if proxy_file:
            working_count = len(proxy_manager.proxy_list) if proxy_manager.proxy_list else 0
            print(f"\nContinue with {working_count} working proxies? (y/n): ", end="")
            choice = input().strip().lower()
            
            if choice != 'y':
                print("Aborted.")
                sys.exit(0)
            
            print("\nHow many URLs to generate? (press Enter for default): ", end="")
            count_input = input().strip()
            if count_input:
                try:
                    count = int(count_input)
                except ValueError:
                    print("Invalid number, using default")
    except (FileNotFoundError, ValueError) as e:
        print(f"Proxy error: {e}")
        sys.exit(1)
    
    classifier = URLClassifier()
    generator = TinyURLGenerator(logger)
    checker = LinkChecker(proxy_manager, logger)
    
    print(f"Generating {count} TinyURL candidates with pattern: {pattern}")
    
    try:
        candidates = generator.generate_candidates(pattern, count)
        print(f"Generated {len(candidates)} candidates")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    if args.skip_validation:
        print("Skipping validation (--skip-validation flag set)")
        return
    
    print("\nValidating and checking redirects...")
    
    uhq_count = 0
    hq_count = 0
    bad_count = 0
    not_found_count = 0
    
    for url in candidates:
        exists = checker.check_existence(url)
        
        if not exists:
            not_found_count += 1
            continue
        
        destination = checker.get_redirect_destination(url)
        
        if destination:
            tier = classifier.classify(destination)
            logger.log_classification(destination, tier)
            
            if tier == "UHQ":
                uhq_count += 1
            elif tier == "HQ":
                hq_count += 1
            else:
                bad_count += 1
    
    print("\n" + "=" * 50)
    print("Summary Statistics")
    print("=" * 50)
    print(f"Total candidates generated: {len(candidates)}")
    print(f"Not found: {not_found_count}")
    print(f"UHQ URLs: {uhq_count}")
    print(f"HQ URLs: {hq_count}")
    print(f"BAD URLs: {bad_count}")
    print(f"Log file: {log_file}")
    print(f"UHQ file: logs/uhq.txt")
    print(f"HQ file: logs/hq.txt")
    print(f"BAD file: logs/bad.txt")
    print("=" * 50)


if __name__ == "__main__":
    main()
