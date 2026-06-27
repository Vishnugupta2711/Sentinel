import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const OUT_DIR = 'docs/product/screenshots';
const BASE_URL = 'http://127.0.0.1:3000';

if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
}

// 1920x1080 for professional presentation
const viewport = { width: 1920, height: 1080 };

const routes = [
  { name: 'mission_control', path: '/' },
  { name: 'vision', path: '/vision' },
  { name: 'risk_panel', path: '/risk' },
  { name: 'prediction', path: '/prediction' },
  { name: 'planner', path: '/planner' },
  { name: 'compliance', path: '/compliance' },
  { name: 'timeline', path: '/timeline' },
  { name: 'plant_map', path: '/plant-map' }
];

async function captureScreenshots() {
  console.log('Launching browser...');
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();

  for (const route of routes) {
    console.log(`Navigating to ${route.name} (${BASE_URL}${route.path})...`);
    try {
      await page.goto(`${BASE_URL}${route.path}`, { waitUntil: 'networkidle' });
      // Wait a bit extra for websockets / animations to settle
      await page.waitForTimeout(2000);
      
      const outPath = path.join(OUT_DIR, `${route.name}.png`);
      await page.screenshot({ path: outPath, fullPage: true });
      console.log(`Saved screenshot: ${outPath}`);
    } catch (err) {
      console.error(`Failed to capture ${route.name}:`, err.message);
    }
  }

  await browser.close();
  console.log('Finished capturing screenshots.');
}

captureScreenshots();
