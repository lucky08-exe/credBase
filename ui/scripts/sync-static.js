import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const outDir = path.resolve(__dirname, '../out')
const staticDir = path.resolve(__dirname, '../../static')

console.log(`Syncing ${outDir} -> ${staticDir}...`)

if (!fs.existsSync(outDir)) {
  console.error(`Error: ${outDir} does not exist. Run "pnpm build" first.`)
  process.exit(1)
}

// Clean static dir
if (fs.existsSync(staticDir)) {
  fs.rmSync(staticDir, { recursive: true, force: true })
}
fs.mkdirSync(staticDir, { recursive: true })

// Copy all files from out/ to static/
fs.cpSync(outDir, staticDir, { recursive: true })

console.log(`✓ Successfully updated static/ with new UI build!`)
