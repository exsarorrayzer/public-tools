from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Button, Input, Static, Label, Header, Footer, Log, ProgressBar
from textual.binding import Binding
from textual import on
from textual.reactive import reactive
from pathlib import Path
from typing import Optional
import asyncio

from src.logger import Logger
from src.proxy_manager import ProxyManager
from src.url_classifier import URLClassifier
from src.tinyurl_generator import TinyURLGenerator
from src.link_checker import LinkChecker
from src.models import ProxyConfig


class StatsPanel(Static):
    total = reactive(0)
    uhq = reactive(0)
    hq = reactive(0)
    bad = reactive(0)
    not_found = reactive(0)

    def render(self):
        return f"""[bold cyan]Statistics[/bold cyan]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[yellow]Total Generated:[/yellow]  {self.total}
[red]Not Found:[/red]        {self.not_found}
[green]UHQ URLs:[/green]         {self.uhq}
[blue]HQ URLs:[/blue]          {self.hq}
[dim]BAD URLs:[/dim]         {self.bad}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""


class TinyURLApp(App):
    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        height: 100%;
        padding: 1 2;
    }

    #config-panel {
        height: auto;
        border: solid $primary;
        padding: 1 2;
        margin-bottom: 1;
    }

    #stats-panel {
        height: 11;
        border: solid $accent;
        padding: 1 2;
        margin-bottom: 1;
    }

    #log-panel {
        height: 1fr;
        border: solid $secondary;
        padding: 0;
    }

    #action-buttons {
        height: auto;
        margin-top: 1;
    }

    Input {
        margin: 0 1;
    }

    Button {
        margin: 0 1;
        width: 20;
    }

    Label {
        padding: 0 1;
        width: 20;
    }

    .config-row {
        height: auto;
        margin-bottom: 1;
    }

    Log {
        height: 100%;
        border: none;
    }

    ProgressBar {
        margin: 1 2;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("g", "generate", "Generate"),
        Binding("c", "clear_log", "Clear Log"),
    ]

    def __init__(self):
        super().__init__()
        self.logger = None
        self.proxy_manager = None
        self.classifier = None
        self.generator = None
        self.checker = None
        self._is_running = False

    def compose(self) -> ComposeResult:
        yield Header()
        
        with Container(id="main-container"):
            with Vertical(id="config-panel"):
                yield Label("[bold]Configuration[/bold]")
                
                with Horizontal(classes="config-row"):
                    yield Label("Pattern:")
                    yield Input(
                        value=r"https://tinyurl\.com/[a-z0-9]{7}",
                        id="pattern-input",
                        placeholder="Regex pattern"
                    )
                
                with Horizontal(classes="config-row"):
                    yield Label("Count:")
                    yield Input(
                        value="10",
                        id="count-input",
                        placeholder="Number of URLs"
                    )
                
                with Horizontal(classes="config-row"):
                    yield Label("Log File:")
                    yield Input(
                        value="logs/tinyurl.log",
                        id="log-file-input",
                        placeholder="Log file path"
                    )
                
                with Horizontal(classes="config-row"):
                    yield Label("Proxy Host:")
                    yield Input(
                        value="",
                        id="proxy-host-input",
                        placeholder="Optional proxy host"
                    )
                
                with Horizontal(classes="config-row"):
                    yield Label("Proxy Port:")
                    yield Input(
                        value="",
                        id="proxy-port-input",
                        placeholder="Optional proxy port"
                    )
                
                with Horizontal(classes="config-row"):
                    yield Label("Proxy File:")
                    yield Input(
                        value="",
                        id="proxy-file-input",
                        placeholder="Optional proxy list file (host:port per line)"
                    )
            
            with Container(id="stats-panel"):
                yield StatsPanel(id="stats")
            
            with Container(id="log-panel"):
                yield Log(id="log-output")
            
            with Horizontal(id="action-buttons"):
                yield Button("Generate", variant="primary", id="generate-btn")
                yield Button("Clear Log", variant="default", id="clear-btn")
                yield Button("Quit", variant="error", id="quit-btn")
        
        yield Footer()

    def on_mount(self):
        self.title = "TinyURL Generator & Checker"
        log = self.query_one("#log-output", Log)
        log.write_line("[bold green]Ready[/bold green]")

    @on(Button.Pressed, "#generate-btn")
    async def handle_generate(self):
        await self.action_generate()

    @on(Button.Pressed, "#clear-btn")
    def handle_clear(self):
        self.action_clear_log()

    @on(Button.Pressed, "#quit-btn")
    def handle_quit(self):
        self.action_quit()

    async def action_generate(self):
        if self._is_running:
            return
        
        self._is_running = True
        log = self.query_one("#log-output", Log)
        stats = self.query_one("#stats", StatsPanel)
        
        pattern_input = self.query_one("#pattern-input", Input)
        count_input = self.query_one("#count-input", Input)
        log_file_input = self.query_one("#log-file-input", Input)
        proxy_host_input = self.query_one("#proxy-host-input", Input)
        proxy_port_input = self.query_one("#proxy-port-input", Input)
        
        pattern = pattern_input.value
        try:
            count = int(count_input.value)
        except ValueError:
            log.write_line("[red]Error: Count must be a number[/red]")
            self._is_running = False
            return
        
        log_file = log_file_input.value
        proxy_host = proxy_host_input.value.strip()
        proxy_port_str = proxy_port_input.value.strip()
        proxy_file_input = self.query_one("#proxy-file-input", Input)
        proxy_file = proxy_file_input.value.strip()
        
        proxy_config = None
        proxy_file_path = None
        
        if proxy_file:
            proxy_file_path = proxy_file
            log.write_line(f"[cyan]Loading proxies from: {proxy_file}[/cyan]")
        elif proxy_host and proxy_port_str:
            try:
                proxy_port = int(proxy_port_str)
                proxy_config = ProxyConfig(host=proxy_host, port=proxy_port, protocol="http")
                log.write_line(f"[cyan]Using proxy: {proxy_host}:{proxy_port}[/cyan]")
            except ValueError:
                log.write_line("[red]Error: Proxy port must be a number[/red]")
                self._is_running = False
                return
        
        try:
            self.logger = Logger(log_file)
            self.proxy_manager = ProxyManager(proxy_config, proxy_file_path)
            
            if proxy_file_path and self.proxy_manager.proxy_list:
                log.write_line(f"[green]Loaded {len(self.proxy_manager.proxy_list)} proxies[/green]")
            
            self.classifier = URLClassifier()
            self.generator = TinyURLGenerator(self.logger)
            self.checker = LinkChecker(self.proxy_manager, self.logger)
            
            log.write_line(f"[bold yellow]Generating {count} URLs with pattern: {pattern}[/bold yellow]")
            
            candidates = self.generator.generate_candidates(pattern, count)
            stats.total = len(candidates)
            
            log.write_line(f"[green]Generated {len(candidates)} candidates[/green]")
            
            stats.uhq = 0
            stats.hq = 0
            stats.bad = 0
            stats.not_found = 0
            
            for idx, url in enumerate(candidates, 1):
                log.write_line(f"[dim]Checking {idx}/{len(candidates)}: {url}[/dim]")
                
                exists = await asyncio.to_thread(self.checker.check_existence, url)
                
                if not exists:
                    stats.not_found += 1
                    log.write_line(f"[red]✗[/red] {url} - Not found")
                    continue
                
                destination = await asyncio.to_thread(self.checker.get_redirect_destination, url)
                
                if destination:
                    tier = self.classifier.classify(destination)
                    self.logger.log_classification(destination, tier)
                    
                    if tier == "UHQ":
                        stats.uhq += 1
                        log.write_line(f"[bold green]✓ UHQ[/bold green] {url} → {destination}")
                    elif tier == "HQ":
                        stats.hq += 1
                        log.write_line(f"[bold blue]✓ HQ[/bold blue] {url} → {destination}")
                    else:
                        stats.bad += 1
                        log.write_line(f"[dim]✓ BAD[/dim] {url} → {destination}")
                else:
                    stats.not_found += 1
            
            log.write_line("[bold green]═══════════════════════════════════════[/bold green]")
            log.write_line("[bold green]Generation Complete![/bold green]")
            log.write_line(f"[cyan]Log saved to: {self.log_file}[/cyan]")
            log.write_line(f"[cyan]UHQ URLs saved to: logs/uhq.txt[/cyan]")
            log.write_line(f"[cyan]HQ URLs saved to: logs/hq.txt[/cyan]")
            log.write_line(f"[cyan]BAD URLs saved to: logs/bad.txt[/cyan]")
            log.write_line("[bold green]═══════════════════════════════════════[/bold green]")
            
        except ValueError as e:
            log.write_line(f"[bold red]Error: {e}[/bold red]")
        except Exception as e:
            log.write_line(f"[bold red]Unexpected error: {e}[/bold red]")
        finally:
            self._is_running = False

    def action_clear_log(self):
        log = self.query_one("#log-output", Log)
        log.clear()
        log.write_line("[bold green]Log cleared[/bold green]")

    def action_quit(self):
        self.exit()


def main():
    app = TinyURLApp()
    app.run()


if __name__ == "__main__":
    main()
