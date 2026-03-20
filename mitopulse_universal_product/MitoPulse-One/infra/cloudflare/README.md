# Cloudflare Tunnel (Optional) — Global Demo

If you want the PWA + Dashboard accessible from anywhere (partners, investors),
you can expose your local ports using Cloudflare Tunnel.

## Manual
Backend:
```bash
cloudflared tunnel --url http://localhost:8000
```

Webapp:
```bash
cloudflared tunnel --url http://localhost:5176
```

Share the generated HTTPS URLs.

