# CODDED BY RAYZER
import asyncio  # By Rayzer
import websockets  # By Rayzer
import json  # By Rayzer
from rich.console import Console  # By Rayzer
from rich.panel import Panel  # By Rayzer
import requests  # By Rayzer
import os  # By Rayzer
import sys  # By Rayzer

console = Console()  # By Rayzer

GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"  # By Rayzer

def get_token_from_file():  # By Rayzer
    current_dir = os.path.dirname(os.path.abspath(__file__))  # By Rayzer
    token_path = os.path.join(current_dir, "token.txt")  # By Rayzer
    if not os.path.exists(token_path):  # By Rayzer
        console.print(f"[red]Cant Find token.txt Needed Path: {token_path}[/red]")  # By Rayzer
        input("Press Enter")  # By Rayzer
        sys.exit(1)  # By Rayzer
    with open(token_path, "r") as f:  # By Rayzer
        return f.read().strip()  # By Rayzer

def get_user_info(token):  # By Rayzer
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }  # By Rayzer
    response = requests.get("https://discord.com/api/v10/users/@me", headers=headers)  # By Rayzer
    if response.status_code == 200:  # By Rayzer
        user = response.json()  # By Rayzer
        info = f"""
[bold green]Account Info:[/bold green]
[cyan]Username:[/cyan] {user.get('username')}#{user.get('discriminator')}
[cyan]ID:[/cyan] {user.get('id')}
[cyan]Email:[/cyan] {user.get('email', 'None')}
[cyan]Phone:[/cyan] {user.get('phone', 'None')}
"""  # By Rayzer
        console.print(Panel(info.strip(), title="Token Info", subtitle="# By Rayzer"))  # By Rayzer
    else:
        console.print("[red]Token Is Invalid.[/red]")  # By Rayzer
        sys.exit(1)  # By Rayzer

async def keep_online(token):  # By Rayzer
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Origin": "https://discord.com",
        "Referer": "https://discord.com/channels/@me"
    }  # By Rayzer

    while True:  # By Rayzer
        try:  # By Rayzer
            async with websockets.connect(GATEWAY_URL, extra_headers=headers) as ws:  # By Rayzer

                hello = await ws.recv()  # By Rayzer
                hello_data = json.loads(hello)  # By Rayzer

                heartbeat_interval = hello_data['d']['heartbeat_interval'] / 1000  # By Rayzer

                identify_payload = {
                    "op": 2,
                    "d": {
                        "token": token,
                        "properties": {
                            "$os": "Linux",
                            "$browser": "Discord Client",
                            "$device": "Linux"
                        },
                        "presence": {
                            "status": "online",
                            "afk": False,
                            "since": 0,
                            "activities": []
                        },
                        "compress": False
                    }
                }  # By Rayzer

                await ws.send(json.dumps(identify_payload))  # By Rayzer
                console.print("[green]Connected To Account. For Exit CTRL+C[/green]")  # By Rayzer

                async def send_heartbeat():  # By Rayzer
                    while True:  # By Rayzer
                        await asyncio.sleep(heartbeat_interval)  # By Rayzer
                        await ws.send(json.dumps({"op": 1, "d": None}))  # By Rayzer

                await send_heartbeat()  # By Rayzer

        except websockets.exceptions.ConnectionClosedError as e:  # By Rayzer
            console.print(f"[yellow]Disconnected. Trying To Connect Again[/yellow]")  # By Rayzer
            await asyncio.sleep(5)  # By Rayzer
            continue  # By Rayzer

if __name__ == "__main__":  # By Rayzer
    console.print(Panel("[bold blue]Discord Token Onliner[/bold blue]", title="Rayzer Token Onliner", subtitle="CTRL+C For Exit"))  # By Rayzer
    try:  # By Rayzer
        token = get_token_from_file()  # By Rayzer
        get_user_info(token)  # By Rayzer
        asyncio.run(keep_online(token))  # By Rayzer
    except KeyboardInterrupt:  # By Rayzer
        console.print("\n[red]Quit[/red]")  # By Rayzer
