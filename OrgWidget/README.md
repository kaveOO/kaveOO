# Organization Widget Server

A Dracula-themed GitHub organization stats widget server.

## Deploy to Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Login: `vercel login`
3. Deploy: `vercel`

## Deploy to Railway

1. Visit [railway.app](https://railway.app)
2. Connect your GitHub repo
3. Deploy the `org-widget` folder

## Deploy to Render

1. Visit [render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repo
4. Set build command: `npm install`
5. Set start command: `node server.js`

## Usage

After deployment, update your README.md with your deployed URL:

```markdown
<img src="https://your-deployed-url.vercel.app/org/1337Corporation" alt="1337Corporation Organization Widget" height="120" />
```
