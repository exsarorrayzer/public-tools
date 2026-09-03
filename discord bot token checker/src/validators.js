import axios from 'axios';
import { readFile } from 'fs/promises';

export const validateToken = async (token) => {
  try {
    const response = await axios.get('https://discord.com/api/v10/users/@me', {
      headers: {
        'Authorization': `Bot ${token}`
      }
    });
    return response.status === 200;
  } catch (error) {
    return false;
  }
};

export const checkTokenStatus = async (token) => {
  return await validateToken(token);
};

export const validateTokensFromFile = async (filePath) => {
  try {
    const content = await readFile(filePath, 'utf-8');
    const tokens = content
      .split('\n')
      .map(line => line.trim())
      .filter(line => line && !line.startsWith('#'));

    const results = [];

    for (const token of tokens) {
      try {
        const response = await axios.get('https://discord.com/api/v10/users/@me', {
          headers: {
            'Authorization': `Bot ${token}`
          }
        });

        if (response.status === 200) {
          results.push({
            token,
            valid: true,
            username: response.data.username,
            id: response.data.id
          });
        }
      } catch (error) {
        results.push({
          token,
          valid: false
        });
      }
    }

    return results;
  } catch (error) {
    throw new Error(`Failed to read file: ${error.message}`);
  }
};
