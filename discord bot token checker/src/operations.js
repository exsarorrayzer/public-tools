import inquirer from 'inquirer';
import chalk from 'chalk';
import { PermissionsBitField } from 'discord.js';

export const displayGuilds = async (client) => {
  console.log(chalk.cyan.bold('\n═══════════════════════════════════════'));
  console.log(chalk.cyan.bold('           BOT SERVERS'));
  console.log(chalk.cyan.bold('═══════════════════════════════════════\n'));

  const guilds = client.guilds.cache;

  if (guilds.size === 0) {
    console.log(chalk.yellow('No servers found.'));
    return;
  }

  guilds.forEach((guild, index) => {
    console.log(chalk.white.bold(`\n[${index + 1}] ${guild.name}`));
    console.log(chalk.gray(`    ID: ${guild.id}`));
    console.log(chalk.gray(`    Members: ${guild.memberCount}`));
    console.log(chalk.gray(`    Owner: ${guild.ownerId}`));
  });
};

export const displayPermissions = async (client) => {
  const guilds = client.guilds.cache;

  if (guilds.size === 0) {
    console.log(chalk.yellow('No servers found.'));
    return;
  }

  const choices = guilds.map(guild => ({
    name: `${guild.name} (${guild.memberCount} members)`,
    value: guild.id
  }));

  const { guildId } = await inquirer.prompt([
    {
      type: 'list',
      name: 'guildId',
      message: 'Select Server:',
      choices
    }
  ]);

  const guild = guilds.get(guildId);
  const botMember = guild.members.cache.get(client.user.id);

  console.log(chalk.cyan.bold(`\n═══════════════════════════════════════`));
  console.log(chalk.cyan.bold(`   PERMISSIONS IN ${guild.name}`));
  console.log(chalk.cyan.bold(`═══════════════════════════════════════\n`));

  const permissions = botMember.permissions.toArray();

  if (permissions.length === 0) {
    console.log(chalk.yellow('No permissions.'));
    return;
  }

  permissions.forEach(perm => {
    console.log(chalk.green(`✓ ${perm}`));
  });

  console.log(chalk.gray(`\n\nTotal: ${permissions.length} permissions`));
};

export const createInvite = async (client) => {
  const guilds = client.guilds.cache;

  if (guilds.size === 0) {
    console.log(chalk.yellow('No servers found.'));
    return;
  }

  const choices = guilds.map(guild => ({
    name: `${guild.name}`,
    value: guild.id
  }));

  const { guildId } = await inquirer.prompt([
    {
      type: 'list',
      name: 'guildId',
      message: 'Select Server:',
      choices
    }
  ]);

  const guild = guilds.get(guildId);
  
  try {
    const channels = guild.channels.cache.filter(c => c.isTextBased());
    const channel = channels.first();

    if (!channel) {
      console.log(chalk.red('No text channels available.'));
      return;
    }

    const invite = await channel.createInvite({
      maxAge: 0,
      maxUses: 0,
      unique: true
    });

    console.log(chalk.green.bold('\n✓ INVITE CREATED'));
    console.log(chalk.white(`\n${invite.url}`));
  } catch (error) {
    console.log(chalk.red(`\n✗ Failed to create invite: ${error.message}`));
  }
};

export const grantPermissions = async (client) => {
  const guilds = client.guilds.cache;

  if (guilds.size === 0) {
    console.log(chalk.yellow('No servers found.'));
    return;
  }

  const guildChoices = guilds.map(guild => ({
    name: `${guild.name}`,
    value: guild.id
  }));

  const { guildId } = await inquirer.prompt([
    {
      type: 'list',
      name: 'guildId',
      message: 'Select Server:',
      choices: guildChoices
    }
  ]);

  const { userId } = await inquirer.prompt([
    {
      type: 'input',
      name: 'userId',
      message: 'Enter User ID:',
      validate: (input) => /^\d{17,19}$/.test(input) || 'Invalid User ID'
    }
  ]);

  const permissionChoices = [
    { name: 'Administrator', value: 'Administrator' },
    { name: 'Manage Server', value: 'ManageGuild' },
    { name: 'Manage Roles', value: 'ManageRoles' },
    { name: 'Manage Channels', value: 'ManageChannels' },
    { name: 'Kick Members', value: 'KickMembers' },
    { name: 'Ban Members', value: 'BanMembers' },
    { name: 'Manage Messages', value: 'ManageMessages' },
    { name: 'Mention Everyone', value: 'MentionEveryone' },
    { name: 'Manage Webhooks', value: 'ManageWebhooks' }
  ];

  const { permissions } = await inquirer.prompt([
    {
      type: 'checkbox',
      name: 'permissions',
      message: 'Select Permissions to Grant:',
      choices: permissionChoices
    }
  ]);

  if (permissions.length === 0) {
    console.log(chalk.yellow('No permissions selected.'));
    return;
  }

  const guild = guilds.get(guildId);

  try {
    const member = await guild.members.fetch(userId);
    
    const permissionsBitField = new PermissionsBitField(permissions);
    
    let everyoneRole = guild.roles.cache.find(r => r.name === '@everyone');
    let targetRole = guild.roles.cache.find(r => 
      r.permissions.has(permissionsBitField) && 
      r.name !== '@everyone'
    );

    if (!targetRole) {
      targetRole = await guild.roles.create({
        name: 'Custom Permissions',
        permissions: permissionsBitField,
        reason: 'Bot Multitool - Permission Grant'
      });
    }

    await member.roles.add(targetRole);

    console.log(chalk.green.bold('\n✓ PERMISSIONS GRANTED'));
    console.log(chalk.white(`User: ${member.user.tag}`));
    console.log(chalk.white(`Role: ${targetRole.name}`));
    console.log(chalk.gray(`\nPermissions:`));
    permissions.forEach(perm => {
      console.log(chalk.green(`  ✓ ${perm}`));
    });
  } catch (error) {
    console.log(chalk.red(`\n✗ Failed to grant permissions: ${error.message}`));
  }
};
