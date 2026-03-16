# Cómo dejar todo en línea

1. Ejecuta etapa 1:
```bash
cd stage1_product_demo/infra
docker compose up --build
```

2. Expón el servicio por HTTPS usando:
- Cloudflare Tunnel
- Caddy/Nginx en VPS
- Render / Railway / Fly / VPS propio

3. Abre en el teléfono:
```text
https://tu-dominio.com/app
```

4. Instala la PWA:
- Android / Chrome: Instalar app
- iPhone / Safari: Agregar a pantalla de inicio

5. Abre el dashboard:
```text
https://tu-dominio.com/dashboard
```
