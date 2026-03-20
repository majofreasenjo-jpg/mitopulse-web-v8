import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({
    plugins: [react()],
    server: {
        host: true,
        port: 5180,
        strictPort: true,
        allowedHosts: [
            'smoke-then-manor-cet.trycloudflare.com',
            'whilst-ladder-singer-ringtones.trycloudflare.com'
        ]
    }
})
