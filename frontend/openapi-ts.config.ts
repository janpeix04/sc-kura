import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
    input: {
        path: 'http://localhost:8000/openapi.json'
    },
    output: {
        path: './src/lib/client', postProcess: ['prettier']
    },
    plugins: [
        {
            name: '@hey-api/client-fetch',
            runtimeConfigPath: '../openapi-ts.runtime' // this is relative to the generated client dir and extensionless.
        }
    ]
})