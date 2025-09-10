// Simple Node.js Express server to generate a Dracula-themed SVG widget for a GitHub organization
const express = require('express');
const fetch = require('node-fetch');
const app = express();
const PORT = process.env.PORT || 3000;

// Dracula colors
const dracula = {
  background: '#282a36',
  foreground: '#f8f8f2',
  accent: '#bd93f9',
  green: '#50fa7b',
  pink: '#ff79c6',
  cyan: '#8be9fd',
};

app.get('/org/:org', async (req, res) => {
  const org = req.params.org;
  const apiUrl = `https://api.github.com/orgs/${org}`;
  try {
    const response = await fetch(apiUrl);
    if (!response.ok) throw new Error('Org not found');
    const data = await response.json();
    // SVG widget with no borders, matching official GitHub stats widgets
    const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="500" height="120" viewBox="0 0 500 120" fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <rect width="500" height="120" rx="4.5" fill="${dracula.background}" />
  <text x="25" y="45" fill="${dracula.accent}" font-size="20" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-weight="600">${data.login}</text>
  <text x="25" y="70" fill="${dracula.foreground}" font-size="14" font-family="Segoe UI, Helvetica, Arial, sans-serif">${data.description ? (data.description.length > 55 ? data.description.slice(0, 55) + '...' : data.description) : 'No description'}</text>
  <text x="25" y="95" fill="${dracula.green}" font-size="12" font-family="Segoe UI, Helvetica, Arial, sans-serif">📦 ${data.public_repos} Public repos</text>
  <defs>
    <clipPath id="avatarClip">
      <circle cx="450" cy="60" r="30" />
    </clipPath>
  </defs>
  <image xlink:href="${data.avatar_url}" x="420" y="30" height="60" width="60" clip-path="url(#avatarClip)" />
</svg>`;
    res.setHeader('Content-Type', 'image/svg+xml');
    res.send(svg);
  } catch (err) {
    res.status(404).send('Organization not found');
  }
});

app.listen(PORT, () => {
  console.log(`Org widget server running on port ${PORT}`);
});
