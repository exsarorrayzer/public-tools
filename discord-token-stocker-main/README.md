Discord Account & Bot Manager

<img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
<img src="https://img.shields.io/badge/Python-3.8%2B-blue.svg" alt="Python">
<img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" alt="Platform">

A secure, command-line interface tool for managing Discord bot tokens and user accounts with military-grade encryption. Keep your Discord credentials safe and organized with this powerful local storage solution.

<br>

🚀 Features

🔐 Security

· Custom Encryption: Uses proprietary RayCrypt algorithm for maximum security

· Master Key Protection: All data encrypted with a user-defined master password

· Local Storage: Your data never leaves your computer

· Secure File Permissions: Automatic file permission locking on Unix systems

<br>

🤖 Bot Management

· Secure Token Storage: Encrypt and store multiple bot tokens

· Quick Access: Retrieve tokens instantly when needed

· Organization: Categorize and name your bots for easy management

· Validation: Automatic token format checking

<br>

👤 Account Management

· User Token Storage: Safely store user account tokens

· Account Information: Fetch and display detailed profile information

· Token Validation: Verify token validity before storage

· Bulk Management: Handle multiple accounts efficiently

<br>

💻 CLI Interface

· Intuitive Commands: Simple, memorable command structure

· Tab Completion: Works with shell autocompletion

· Silent Operation: No unnecessary output, perfect for scripting

· Cross-Platform: Works on Windows, Linux, and macOS

<br>

📦 Installation

Prerequisites

· Python 3.8 or higher

· pip (Python package manager)

<br>

Step-by-Step Installation

1. Clone the Repository
   ```bash
   git clone https://github.com/exsarorrayzer/discord-token-stocker
   cd discord-token-stocker
   ```
2. Install Dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Verify Installation
   ```bash
   python main.py --help
   ```

<br>

🛠️ Usage

First Time Setup

When you run the tool for the first time, you'll be prompted to create a master key:

```bash
python main.py bot list
```

You'll see:

```
🔐 No master key found. Creating new secure storage.
Create a master key: 
Confirm master key: 
✓ Master key created successfully!
No bots stored.
```

<br>

Bot Management Commands

· Add a Bot Token

```bash
python main.py bot add my-awesome-bot
```

· List All Bots

```bash
python main.py bot list
```

· Show Bot Token

```bash
python main.py bot show my-awesome-bot
```

· Remove a Bot

```bash
python main.py bot remove my-awesome-bot
```

<br>

Account Management Commands

· Add a User Account

```bash
python main.py account add my-personal-account
```

· List All Accounts

```bash
python main.py account list
```

· Get Account Information

```bash
python main.py account info my-personal-account
```

· Remove an Account

```bash
python main.py account remove my-personal-account
```

<br>

Utility Commands

· View Statistics

```bash
python main.py stats
```

· Get Help

```bash
python main.py --help
```

<br>

📁 Project Structure

```
discord-token-stocker/
│
├── src/
│   ├── __init__.py
│   ├── crypt.py          # RayCrypt encryption engine
│   ├── manager.py        # Core management logic
│   └── cli.py           # Command-line interface
│
├── accounts.dat         # Encrypted data storage (auto-created)
├── master.key          # Master key file (auto-created)
├── requirements.txt    # Python dependencies
├── LICENSE            # MIT License
└── main.py           # Entry point
```

<br>

🔧 Technical Details

Encryption System

The tool uses a custom RayCrypt algorithm that provides:

· XOR-based byte manipulation

· Base64 encoding for safe storage

· Key-based encryption/decryption

· Protection against common attacks

Data Storage

· All tokens stored in encrypted accounts.dat file

· Master key stored separately in master.key

· File permissions automatically secured (600 on Unix systems)

· No internet connectivity required for operation

API Integration

· Uses Discord's official API v10

· Validates tokens against Discord's servers

· Fetches user profile information securely

· Respects Discord's rate limits

<br>

🛡️ Security Considerations

· Master Key Security: Your master key is the only way to decrypt your data. Keep it safe and never share it.

· File Locations: The tool creates files in the current directory. Consider using secure locations for production use.

· Token Safety: Discord tokens provide full access to accounts/bots. This tool encrypts them, but physical access to your computer could still compromise security.

· Backup Strategy: Regularly backup your accounts.dat file and master key separately.

<br>

🤝 Contributing

We welcome contributions! Please feel free to submit pull requests, report bugs, or suggest new features.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

<br>

📄 License

This project is licensed under the MIT License - see the <a href="LICENSE">LICENSE</a> file for details.

<br>

⚠️ Disclaimer

This tool is designed for legitimate Discord developers and users to manage their own tokens.

· Always comply with Discord's Terms of Service

· Only store tokens for accounts you own

· Use responsibly and ethically

· The developers are not responsible for misuse of this tool

<br>

🆘 Support

If you encounter any issues or have questions:

1. Check the command help: python main.py --help
2. Review the issue tracker on GitHub
3. Ensure you're using Python 3.8 or higher
4. Verify your master key is correct

<br>

---

<div align="center">

Made with ❤️ by exsarorrayzer

<img src="https://img.shields.io/badge/Version-1.0.0-orange.svg" alt="Version">
<img src="https://img.shields.io/badge/Last%20Updated-January%202025-yellow.svg" alt="Last Updated">

</div>