/**
 * Icon Generation Script
 * 
 * This script provides instructions for generating icons from the SVG source.
 * 
 * To generate icons, you'll need to:
 * 1. Install icon generation tools (optional):
 *    npm install -g electron-icon-maker
 * 
 * 2. Or use online converters:
 *    - https://cloudconvert.com/svg-to-ico (for .ico)
 *    - https://cloudconvert.com/svg-to-icns (for .icns)
 *    - https://cloudconvert.com/svg-to-png (for .png at 512x512)
 * 
 * 3. Manual generation with ImageMagick (if installed):
 *    convert build/icon.svg -resize 256x256 build/icon.ico
 *    convert build/icon.svg -resize 512x512 build/icon.png
 * 
 * 4. Place generated files in build/ folder:
 *    - build/icon.ico (Windows)
 *    - build/icon.icns (macOS)
 *    - build/icon.png (Linux, 512x512)
 * 
 * The SVG source is at: build/icon.svg
 */

const fs = require('fs');
const path = require('path');

console.log('╔════════════════════════════════════════════════════════════╗');
console.log('║  Frozen Peak Solutions - Icon Generation Guide            ║');
console.log('╚════════════════════════════════════════════════════════════╝');
console.log('');
console.log('✓ SVG icon created: build/icon.svg');
console.log('✓ Favicon created: public/favicon.svg');
console.log('');
console.log('To generate platform-specific icons:');
console.log('');
console.log('Option 1 - Online Converters (Easiest):');
console.log('  1. Go to https://cloudconvert.com/svg-to-ico');
console.log('  2. Upload build/icon.svg');
console.log('  3. Convert to .ico (256x256) and save as build/icon.ico');
console.log('  4. Repeat for .icns (macOS) and .png (512x512 for Linux)');
console.log('');
console.log('Option 2 - electron-icon-maker (Automated):');
console.log('  npm install -g electron-icon-maker');
console.log('  electron-icon-maker --input=build/icon.svg --output=build');
console.log('');
console.log('Option 3 - ImageMagick (Command Line):');
console.log('  convert build/icon.svg -resize 256x256 build/icon.ico');
console.log('  convert build/icon.svg -resize 512x512 build/icon.png');
console.log('');
console.log('Current status:');

const buildDir = path.join(__dirname, '..', 'build');
const icons = {
  'icon.svg': 'SVG source (all platforms)',
  'icon.ico': 'Windows',
  'icon.icns': 'macOS',
  'icon.png': 'Linux'
};

Object.entries(icons).forEach(([file, platform]) => {
  const exists = fs.existsSync(path.join(buildDir, file));
  const status = exists ? '✓' : '✗';
  const color = exists ? '\x1b[32m' : '\x1b[31m';
  console.log(`  ${color}${status}\x1b[0m ${file.padEnd(15)} (${platform})`);
});

console.log('');
console.log('Brand Colors:');
console.log('  Primary:   #87CEEB (Sky Blue)');
console.log('  Secondary: #B0E0E6 (Powder Blue)');
console.log('  Dark:      #0f2027 - #2c5364 (Mountain gradient)');
console.log('');
