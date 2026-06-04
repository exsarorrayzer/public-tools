import os
import json
import requests
import getpass
from .crypt import RayCrypt

class DiscordAccountManager:
    def __init__(self, storage_file="accounts.dat", key_file="master.key"):
        self.storage_file = storage_file
        self.key_file = key_file
        self.crypt = RayCrypt()
        self.master_key = self._load_or_create_master_key()
        self.data = self._load_data()
    
    def _load_or_create_master_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, 'r') as f:
                return f.read().strip()
        else:
            print("🔐 No master key found. Creating new secure storage.")
            master_key = getpass.getpass("Create a master key: ")
            confirm_key = getpass.getpass("Confirm master key: ")
            
            if master_key != confirm_key:
                print("❌ Keys don't match!")
                exit(1)
            
            if len(master_key) < 8:
                print("❌ Master key must be at least 8 characters!")
                exit(1)
                
            with open(self.key_file, 'w') as f:
                f.write(master_key)
            os.chmod(self.key_file, 0o600)
            print("✓ Master key created successfully!")
            return master_key
    
    def _load_data(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    encrypted_data = f.read()
                    decrypted = self.crypt.decrypt(encrypted_data, self.master_key)
                    if "❌ incorrect" in decrypted:
                        print("❌ Wrong master key or corrupted data!")
                        exit(1)
                    return json.loads(decrypted)
            except Exception as e:
                print(f"❌ Error loading data: {e}")
                return {"bots": {}, "accounts": {}}
        return {"bots": {}, "accounts": {}}
    
    def _save_data(self):
        encrypted = self.crypt.encrypt(json.dumps(self.data), self.master_key)
        with open(self.storage_file, 'w') as f:
            f.write(encrypted)
        os.chmod(self.storage_file, 0o600)
    
    # Bot Management Methods
    def add_bot(self, bot_name, token):
        self.data["bots"][bot_name] = token
        self._save_data()
        print(f"✓ Bot '{bot_name}' added successfully")
    
    def get_bot(self, bot_name):
        return self.data["bots"].get(bot_name)
    
    def list_bots(self):
        return list(self.data["bots"].keys())
    
    def remove_bot(self, bot_name):
        if bot_name in self.data["bots"]:
            del self.data["bots"][bot_name]
            self._save_data()
            print(f"✓ Bot '{bot_name}' removed")
        else:
            print(f"✗ Bot '{bot_name}' not found")
    
    # Account Management Methods
    def add_account(self, account_name, token):
        if self._validate_user_token(token):
            self.data["accounts"][account_name] = token
            self._save_data()
            print(f"✓ Account '{account_name}' added successfully")
            return True
        else:
            print("✗ Invalid user token")
            return False
    
    def _validate_user_token(self, token):
        headers = {'Authorization': token}
        try:
            response = requests.get('https://discord.com/api/v10/users/@me', headers=headers)
            return response.status_code == 200
        except:
            return False
    
    def get_account_info(self, account_name):
        token = self.data["accounts"].get(account_name)
        if not token:
            return None
        
        headers = {'Authorization': token}
        try:
            response = requests.get('https://discord.com/api/v10/users/@me', headers=headers)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching account info: {e}")
        return None
    
    def list_accounts(self):
        return list(self.data["accounts"].keys())
    
    def remove_account(self, account_name):
        if account_name in self.data["accounts"]:
            del self.data["accounts"][account_name]
            self._save_data()
            print(f"✓ Account '{account_name}' removed")
        else:
            print(f"✗ Account '{account_name}' not found")
    
    def get_account_stats(self):
        return {
            "total_bots": len(self.data["bots"]),
            "total_accounts": len(self.data["accounts"]),
            "bot_names": list(self.data["bots"].keys()),
            "account_names": list(self.data["accounts"].keys())
        }