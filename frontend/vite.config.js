import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Acepta conexiones desde fuera del contenedor de Docker
    host: true,
    port: 5173,
    watch: {
      // En Docker sobre Windows los cambios de archivos no se notifican solos:
      // hay que revisarlos cada cierto tiempo para que el sitio se recargue.
      usePolling: true,
    },
  },
})
