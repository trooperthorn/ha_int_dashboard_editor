import { nodeResolve } from "@rollup/plugin-node-resolve";
import typescript from "@rollup/plugin-typescript";
import terser from "@rollup/plugin-terser";

export default {
  input: "src/dashboard-editor-panel.ts",
  output: {
    file: "dist/dashboard-editor-panel.js",
    format: "esm",
    inlineDynamicImports: true,
  },
  plugins: [nodeResolve({ browser: true }), typescript({ tsconfig: "./tsconfig.json" }), terser()],
};
