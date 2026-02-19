# CEO Arena Frontend

## Local Development

1. Install dependencies  
`npm ci`

2. Start dev server  
`npm run dev`

3. Frontend URL  
`http://localhost:5173`

The app expects the backend API at `http://localhost:8000/api` by default.

## Build

`npm run build`

## Cloudflare Pages Deploy

This frontend is configured for Cloudflare Pages via `wrangler.jsonc`.

1. Authenticate once  
`npx wrangler login`  
`npx wrangler whoami`

2. Set production API URL in Cloudflare Pages environment variables  
`VITE_API_BASE=https://api.your-domain.com/api`

3. Deploy  
`npm run cf:deploy`

## Local Pages Preview

`npm run cf:dev`

This serves the built `dist` output through Cloudflare Pages local runtime.
