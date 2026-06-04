# CODDED BY RAYZER
import os  # By Rayzer
import subprocess  # By Rayzer

print("\n[+] Setup Started\n")  # By Rayzer

requirements_file = "requirements.txt"  # By Rayzer

if not os.path.exists(requirements_file):  # By Rayzer
    print(f"[!] '{requirements_file}' Cant Find requirements.txt Please Make sure you cloned true version Of repo.")  # By Rayzer
    exit()  # By Rayzer

try:  # By Rayzer
    subprocess.check_call(["pip", "install", "-r", requirements_file])  # By Rayzer
    print("\n[+] Setup Finished Type python main.py For ProxyChecker")  # By Rayzer
except Exception as e:  # By Rayzer
    print(f"[!] Error: {e}")  # By Rayzer
