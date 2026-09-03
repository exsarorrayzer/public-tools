# TinyURL Generator and Checker

Automated TinyURL link generation, validation, and classification system with proxy support ## Features
## Installation

```bash
pip install -r requirements.txt
```

Or with development dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

### Simple TUI (No Dependencies)

```bash
python -m src.tui_simple
```

Lightweight terminal interface without external dependencies.

**Menu Options:**
- `g` - Generate and check URLs
- `c` - Configure settings
- `s` - Show statistics
- `q` - Quit

### Advanced TUI (Textual)

```bash
python -m src.tui
```

Rich terminal interface with real-time updates (requires textual).

**Controls:**
- `g` - Generate URLs
- `c` - Clear log
- `q` - Quit

**Proxy Options:**
- Single proxy: Enter host and port in the form
- Bulk proxies: Provide path to proxy list file (one proxy per line)

**Proxy File Format:**
```
host:port
protocol://host:port
```

Example:
```
127.0.0.1:8080
http://proxy.example.com:8888
https://secure-proxy.com:9999
```

**Controls:**
- `g` - Generate URLs
- `c` - Clear log
- `q` - Quit

### CLI (Command Line)

#### Basic Generation

```bash
python -m src.cli --count 10 --skip-validation
```

#### With Bulk Proxies

```bash
python -m src.cli --count 10 --proxy-file proxies.txt
```

Each request randomly selects a proxy from the file.

#### With Single Proxy

```bash
python -m src.cli --proxy-host proxy.example.com --proxy-port 8080 --count 10
```

## CLI Arguments

- `--pattern` - Regex pattern for URL generation (default: `https://tinyurl\.com/[a-z0-9]{7}`)
- `--count` - Number of candidates to generate (default: 10)
- `--log-file` - Log file path (default: `logs/tinyurl.log`)
- `--proxy-host` - Proxy server host
- `--proxy-port` - Proxy server port
- `--proxy-protocol` - Proxy protocol: http or https (default: http)
- `--proxy-file` - Path to proxy list file (one proxy per line: host:port or protocol://host:port)
- `--skip-validation` - Skip validation and redirect checking

## URL Classification

- **UHQ**: mega.nz, mediafire.com
- **HQ**: justpaste.io, google drive
- **BAD**: All other domains

## Requirements

- Python 3.8+
- requests
- textual (for TUI)
- hypothesis (for property-based testing)
- pytest (for testing)
