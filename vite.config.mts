import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import cssInjectedByJsPlugin from "vite-plugin-css-injected-by-js";
import path from "path";

export default defineConfig({
  plugins: [react(), cssInjectedByJsPlugin()],
  server: {
    port: 5173,
    host: "0.0.0.0",
    cors: true,
  },
  build: {
    outDir: path.resolve(import.meta.dirname, "hunts/static"),
    emptyOutDir: false,
    sourcemap: true,
    rollupOptions: {
      input: path.resolve(import.meta.dirname, "hunts/src/index.tsx"),
      output: {
        entryFileNames: "main.js",
        format: "iife",
      },
    },
  },
});
