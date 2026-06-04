# CODDED BY RAYZER
import os  # By Rayzer
import sys  # By Rayzer

try:
    from rich.console import Console  # By Rayzer
    from rich.panel import Panel  # By Rayzer
    rich_installed = True  # By Rayzer
    console = Console()  # By Rayzer
except ImportError:
    rich_installed = False  # By Rayzer
    console = None  # By Rayzer

def safe_print(msg, title=None):  # By Rayzer
    if rich_installed:
        console.print(Panel(msg, title=title or "Info", subtitle="# By Rayzer", style="bold green"))  # By Rayzer
    else:
        print(f"\n[ {title or 'Bilgi'} ]\n{msg}\n")  # By Rayzer

def install_requirements():  # By Rayzer
    safe_print("Setup Started", "X")  # By Rayzer
    os.system(f"{sys.executable} -m pip install -r requirements.txt")  # By Rayzer

def create_token_file():  # By Rayzer
    if not os.path.exists("token.txt"):  # By Rayzer
        with open("token.txt", "w") as f:  # By Rayzer
            f.write("Place Token Here\n")  # By Rayzer
        safe_print("Created token.txt. Put Your Token in token.txt Be careful Your account can be banned", "File Is ready")  # By Rayzer
    else:
        safe_print("token.txt Is Found On files, Put Your Token in token.txt Be careful Your account can be banned.", "Found token.txt")  # By Rayzer

if __name__ == "__main__":  # By Rayzer
    install_requirements()  # By Rayzer
    create_token_file()  # By Rayzer
    safe_print("Setup Finished You Can Start tool by typing python main.py.", "✅ Ready")  # By Rayzer
