import requests
from rich.console import Console
from rich.panel import Panel

console = Console()

def get_ip_info(ip=None):
    """Fetch detailed information about an IP address using ip-api.com"""
    url = f"http://ip-api.com/json/{ip or ''}?fields=66846719"
    try:
        response = requests.get(url)
        data = response.json()
        
        if data['status'] != 'success':
            console.print("[red]Error: IP not found or API error[/red]")
            return

        ip_info = f"""
[bold green]IP Information:[/bold green]

[bold yellow]🌍 IP:[/bold yellow] {data.get("query", "-")}
[bold yellow]🏙️ Country:[/bold yellow] {data.get("country", "-")} ({data.get("countryCode", "-")})
[bold yellow]🗺️ Region:[/bold yellow] {data.get("regionName", "-")} - {data.get("region", "-")}
[bold yellow]🏠 City:[/bold yellow] {data.get("city", "-")}
[bold yellow]🧭 ZIP Code:[/bold yellow] {data.get("zip", "-")}
[bold yellow]⏰ Timezone:[/bold yellow] {data.get("timezone", "-")}
[bold yellow]⚡ ISP:[/bold yellow] {data.get("isp", "-")}
[bold yellow]💻 Organization:[/bold yellow] {data.get("org", "-")}
[bold yellow]📡 AS (Autonomous System):[/bold yellow] {data.get("as", "-")}
[bold yellow]🔐 Proxy/VPN/Tor:[/bold yellow]
  • Proxy: {"✅" if data.get("proxy") else "❌"}
  • VPN: {"✅" if data.get("hosting") else "❌"}
  • Tor: {"✅" if data.get("mobile") else "❌"}
[bold yellow]🧠 Reverse DNS:[/bold yellow] {data.get("reverse", "None")}
[bold yellow]📱 Mobile Connection:[/bold yellow] {"✅" if data.get("mobile") else "❌"}
"""

        console.print(Panel(ip_info, 
                          title="[bold cyan]IP LOOKUP RESULTS[/bold cyan]", 
                          border_style="bright_magenta"))

    except Exception as e:
        console.print(f"[red]Error occurred:[/red] {str(e)}")

if __name__ == "__main__":
    console.print("[bold blue]Enter IP or leave blank (for your IP):[/bold blue] ", end="")
    user_ip = input()
    get_ip_info(user_ip.strip())
