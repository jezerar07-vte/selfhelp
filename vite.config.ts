import { defineConfig } from 'vitest/config';

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        index: 'index.html',
        services: 'services.html',
        estimator: 'estimator.html',
        contact: 'contact.html',
      },
    },
  },
  test: {
    environment: 'jsdom',
    css: { include: [/style\.css/] },
  },
});
