# Infra notes (optional)
For a real “anywhere in the world” demo:
- Put backend on HTTPS (required for iOS PWA capabilities)
- Use a domain and TLS (Cloudflare, Nginx, Caddy)

Recommended stack:
- VPS + Caddy (auto TLS) + systemd uvicorn
