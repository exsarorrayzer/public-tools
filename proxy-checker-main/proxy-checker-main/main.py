import requests
import threading
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from queue import Queue

console = Console()
proxy_file = "proxies.txt"
working_file = "working.txt"
dead_file = "dead.txt"

proxy_queue = Queue()
working_proxies = []
dead_proxies = []

def load_proxies():
    with open(proxy_file, "r") as f:
        for line in f:
            proxy = line.strip()
            if proxy:
                proxy_queue.put(proxy)

def check_proxy(proxy, progress_task, progress):
    try:
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }
        response = requests.get("https://ipinfo.io/json", proxies=proxies, timeout=5)
        if response.status_code == 200 and "ip" in response.json():
            working_proxies.append(proxy)
            console.log(f"[green]ALIVE:[/green] {proxy}")
        else:
            raise Exception("Bad response")
    except:
        dead_proxies.append(proxy)
        console.log(f"[red]DEAD:[/red] {proxy}")
    finally:
        progress.update(progress_task, advance=1)

def worker(progress_task, progress):
    while not proxy_queue.empty():
        proxy = proxy_queue.get()
        check_proxy(proxy, progress_task, progress)
        proxy_queue.task_done()

def save_results():
    with open(working_file, "w") as w:
        for p in working_proxies:
            w.write(p + "\n")
    with open(dead_file, "w") as d:
        for p in dead_proxies:
            d.write(p + "\n")

def main():
    console.print("[bold blue]Starting Proxy Checker...[/bold blue]")
    load_proxies()

    thread_count = 50
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
    ) as progress:
        task = progress.add_task("Scanning Proxies", total=proxy_queue.qsize())
        threads = []

        for _ in range(thread_count):
            t = threading.Thread(target=worker, args=(task, progress))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    save_results()
    console.print(f"[bold green]Finished , Live Proxies saved to working.txt[/bold green] [cyan]{len(working_proxies)} Working[/cyan], [red]{len(dead_proxies)} Dead[/red]")

if __name__ == "__main__":
    main()















