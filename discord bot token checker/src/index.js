import { Client, GatewayIntentBits, PermissionsBitField } from 'discord.js';
import inquirer from 'inquirer';
import chalk from 'chalk';
import { validateToken, checkTokenStatus, validateTokensFromFile } from './validators.js';
import { displayGuilds, displayPermissions, createInvite, grantPermissions } from './operations.js';

let client = null;
let currentToken = null;

const mainMenu = async () => {
  console.clear();
  console.log(chalk.cyan.bold('\n═══════════════════════════════════════'));
  console.log(chalk.cyan.bold('   DISCORD BOT MANAGEMENT MULTITOOL / github: exsarorrayzer'));
  console.log(chalk.cyan.bold('═══════════════════════════════════════\n'));

  if (currentToken) {
    const status = await checkTokenStatus(currentToken);
    console.log(chalk.green(`✓ Token Status: ${status ? 'LIVE' : 'INVALID'}`));
    if (client && client.user) {
      console.log(chalk.green(`✓ Bot: ${client.user.tag}\n`));
    }
  }

  const { action } = await inquirer.prompt([
    {
      type: 'list',
      name: 'action',
      message: 'Select Operation:',
      choices: [
        { name: '🔑 Validate Token', value: 'validate' },
        { name: '📄 Validate Tokens from File', value: 'validateFile' },
        { name: '🏰 List Servers', value: 'servers', disabled: !client },
        { name: '🛡️  List Permissions', value: 'permissions', disabled: !client },
        { name: '🔗 Create Invite Link', value: 'invite', disabled: !client },
        { name: '👤 Grant User Permissions', value: 'grant', disabled: !client },
        { name: '❌ Exit', value: 'exit' }
      ]
    }
  ]);

  switch (action) {
    case 'validate':
      await handleValidateToken();
      break;
    case 'validateFile':
      await handleValidateFromFile();
      break;
    case 'servers':
      await displayGuilds(client);
      break;
    case 'permissions':
      await displayPermissions(client);
      break;
    case 'invite':
      await createInvite(client);
      break;
    case 'grant':
      await grantPermissions(client);
      break;
    case 'exit':
      if (client) client.destroy();
      console.log(chalk.yellow('\nExiting...'));
      process.exit(0);
  }

  await inquirer.prompt([{ type: 'input', name: 'continue', message: 'Press Enter to continue...' }]);
  await mainMenu();
};

const handleValidateToken = async () => {
  const { token } = await inquirer.prompt([
    {
      type: 'password',
      name: 'token',
      message: 'Enter Discord Bot Token:',
      mask: '*'
    }
  ]);

  console.log(chalk.yellow('\n⏳ Validating token...'));

  const isValid = await validateToken(token);

  if (isValid) {
    currentToken = token;
    
    if (client) {
      client.destroy();
    }

    client = new Client({
      intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMembers
      ]
    });

    try {
      await client.login(token);
      console.log(chalk.green.bold(`\n✓ TOKEN IS LIVE`));
      console.log(chalk.green(`✓ Bot: ${client.user.tag}`));
      console.log(chalk.green(`✓ ID: ${client.user.id}`));
      console.log(chalk.green(`✓ Servers: ${client.guilds.cache.size}`));
    } catch (error) {
      console.log(chalk.red.bold('\n✗ TOKEN IS INVALID'));
      currentToken = null;
      client = null;
    }
  } else {
    console.log(chalk.red.bold('\n✗ TOKEN IS INVALID'));
    currentToken = null;
  }
};

const handleValidateFromFile = async () => {
  const { filePath } = await inquirer.prompt([
    {
      type: 'input',
      name: 'filePath',
      message: 'Enter file path (tokens.txt):',
      default: 'tokens.txt'
    }
  ]);

  console.log(chalk.yellow('\n⏳ Validating tokens from file...'));

  try {
    const results = await validateTokensFromFile(filePath);

    console.log(chalk.cyan.bold('\n═══════════════════════════════════════'));
    console.log(chalk.cyan.bold('       VALIDATION RESULTS'));
    console.log(chalk.cyan.bold('═══════════════════════════════════════\n'));

    results.forEach((result, index) => {
      if (result.valid) {
        console.log(chalk.green.bold(`\n[${index + 1}] ✓ LIVE TOKEN`));
        console.log(chalk.green(`    Bot: ${result.username}`));
        console.log(chalk.green(`    ID: ${result.id}`));
        console.log(chalk.gray(`    Token: ${result.token.substring(0, 30)}...`));
      } else {
        console.log(chalk.red.bold(`\n[${index + 1}] ✗ INVALID TOKEN`));
        console.log(chalk.gray(`    Token: ${result.token.substring(0, 30)}...`));
      }
    });

    const validCount = results.filter(r => r.valid).length;
    const invalidCount = results.length - validCount;

    console.log(chalk.cyan.bold('\n═══════════════════════════════════════'));
    console.log(chalk.white(`Total: ${results.length} | Valid: ${chalk.green(validCount)} | Invalid: ${chalk.red(invalidCount)}`));
    console.log(chalk.cyan.bold('═══════════════════════════════════════\n'));

    if (validCount > 0) {
      const { useToken } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'useToken',
          message: 'Use first valid token for operations?',
          default: true
        }
      ]);

      if (useToken) {
        const firstValid = results.find(r => r.valid);
        if (firstValid) {
          currentToken = firstValid.token;

          if (client) {
            client.destroy();
          }

          client = new Client({
            intents: [
              GatewayIntentBits.Guilds,
              GatewayIntentBits.GuildMembers
            ]
          });

          await client.login(currentToken);
          console.log(chalk.green.bold(`\n✓ Bot loaded: ${client.user.tag}`));
        }
      }
    }
  } catch (error) {
    console.log(chalk.red(`\n✗ Error: ${error.message}`));
  }
};

mainMenu().catch(console.error);
