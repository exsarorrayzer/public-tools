import argparse
import getpass
from .manager import DiscordAccountManager

def setup_parser():
    parser = argparse.ArgumentParser(description='Discord Account & Bot Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Bot commands
    bot_parser = subparsers.add_parser('bot', help='Bot management')
    bot_subparsers = bot_parser.add_subparsers(dest='bot_command')
    
    bot_add = bot_subparsers.add_parser('add', help='Add a bot token')
    bot_add.add_argument('name', help='Bot name')
    bot_add.add_argument('--token', help='Bot token')
    
    bot_list = bot_subparsers.add_parser('list', help='List all bots')
    
    bot_remove = bot_subparsers.add_parser('remove', help='Remove a bot')
    bot_remove.add_argument('name', help='Bot name')
    
    bot_show = bot_subparsers.add_parser('show', help='Show bot token')
    bot_show.add_argument('name', help='Bot name')
    
    # Account commands
    acc_parser = subparsers.add_parser('account', help='Account management')
    acc_subparsers = acc_parser.add_subparsers(dest='account_command')
    
    acc_add = acc_subparsers.add_parser('add', help='Add a user account')
    acc_add.add_argument('name', help='Account name')
    acc_add.add_argument('--token', help='User token')
    
    acc_list = acc_subparsers.add_parser('list', help='List all accounts')
    
    acc_info = acc_subparsers.add_parser('info', help='Get account information')
    acc_info.add_argument('name', help='Account name')
    
    acc_remove = acc_subparsers.add_parser('remove', help='Remove an account')
    acc_remove.add_argument('name', help='Account name')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show storage statistics')
    
    return parser

def main():
    parser = setup_parser()
    args = parser.parse_args()
    manager = DiscordAccountManager()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'bot':
            handle_bot_commands(manager, args)
        elif args.command == 'account':
            handle_account_commands(manager, args)
        elif args.command == 'stats':
            handle_stats_command(manager)
    except Exception as e:
        print(f"❌ Error: {e}")

def handle_bot_commands(manager, args):
    if args.bot_command == 'add':
        token = args.token or getpass.getpass("Enter bot token: ")
        manager.add_bot(args.name, token)
    elif args.bot_command == 'list':
        bots = manager.list_bots()
        if bots:
            print("🤖 Stored Bots:")
            for bot in bots:
                print(f"  • {bot}")
        else:
            print("No bots stored.")
    elif args.bot_command == 'remove':
        manager.remove_bot(args.name)
    elif args.bot_command == 'show':
        token = manager.get_bot(args.name)
        if token:
            print(f"Token for {args.name}: {token}")
        else:
            print(f"Bot '{args.name}' not found.")

def handle_account_commands(manager, args):
    if args.account_command == 'add':
        token = args.token or getpass.getpass("Enter user token: ")
        manager.add_account(args.name, token)
    elif args.account_command == 'list':
        accounts = manager.list_accounts()
        if accounts:
            print("👤 Stored Accounts:")
            for acc in accounts:
                print(f"  • {acc}")
        else:
            print("No accounts stored.")
    elif args.account_command == 'info':
        info = manager.get_account_info(args.name)
        if info:
            print(f"📋 Account Info for {args.name}:")
            print(f"  Username: {info['username']}#{info['discriminator']}")
            print(f"  ID: {info['id']}")
            print(f"  Email: {info.get('email', 'N/A')}")
            print(f"  Verified: {info.get('verified', 'N/A')}")
        else:
            print(f"Account '{args.name}' not found or invalid token.")
    elif args.account_command == 'remove':
        manager.remove_account(args.name)

def handle_stats_command(manager):
    stats = manager.get_account_stats()
    print("📊 Storage Statistics:")
    print(f"  Total Bots: {stats['total_bots']}")
    print(f"  Total Accounts: {stats['total_accounts']}")
    print(f"  Bots: {', '.join(stats['bot_names']) or 'None'}")
    print(f"  Accounts: {', '.join(stats['account_names']) or 'None'}")

if __name__ == "__main__":
    main()