import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    css: { include: [/style\.css/] },
  },
});
