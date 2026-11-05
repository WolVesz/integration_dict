import { defineConfig } from '@playwright/test'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  testDir: './e2e',
  workers: 1,
  use: { baseURL: 'http://127.0.0.1:8766', trace: 'retain-on-failure', screenshot: 'only-on-failure' },
  webServer: {
    command: 'python -m uvicorn backend.main:app --host 127.0.0.1 --port 8766',
    cwd: fileURLToPath(new URL('..', import.meta.url)),
    env: { DEV_MODE: 'true', DATABASE_URL: 'sqlite:////tmp/integration-dict-browser.sqlite' },
    url: 'http://127.0.0.1:8766/healthz',
    reuseExistingServer: false,
  },
})
