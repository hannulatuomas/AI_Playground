# Frozen Peak Solutions - Icon Assets

This directory contains the icon assets for LocalAPI.

## Brand Identity

**Company:** Frozen Peak Solutions  
**Theme:** Mountain peak, ice, clarity, precision

## Color Palette

- **Primary:** Sky Blue (#87CEEB)
- **Secondary:** Powder Blue (#B0E0E6)
- **Accent:** Light Blue (#ADD8E6)
- **Background:** Dark Mountain Gradient (#0f2027 → #203a43 → #2c5364)
- **Text:** Ice Blue (#e8f4f8)

## Icon Files

### Source
- `icon.svg` - Master SVG icon (512x512) 

### Platform-Specific Icons (To be generated)
- `icon.ico` - Windows icon (256x256)
- `icon.icns` - macOS icon bundle
- `icon.png` - Linux icon (512x512)

## Generating Platform Icons

Run the following command for instructions:
```bash
npm run icons:info
```

### Quick Generation Options

**Option 1 - Online (Easiest):**
1. Visit https://cloudconvert.com/svg-to-ico
2. Upload `build/icon.svg`
3. Convert and download as `icon.ico`, `icon.icns`, and `icon.png`

**Option 2 - electron-icon-maker:**
```bash
npm install -g electron-icon-maker
electron-icon-maker --input=build/icon.svg --output=build
```

**Option 3 - ImageMagick:**
```bash
convert build/icon.svg -resize 256x256 build/icon.ico
convert build/icon.svg -resize 512x512 build/icon.png
```

## Icon Design

The icon features:
- Three layered mountain peaks representing strength and elevation
- Ice blue gradient (#B0E0E6 → #87CEEB → #ADD8E6)
- Snow caps on peaks for the "frozen" theme
- Dark mountain background for contrast
- Subtle API bracket symbols
- Sparkle effects for ice/clarity theme

## Usage

Icons are automatically used by electron-builder during packaging:
- Windows: `icon.ico`
- macOS: `icon.icns`
- Linux: `icon.png`

The favicon (`public/favicon.svg`) is used in the browser window.

## Required Icons

To build the application, you need to add the following icon files:

### Windows
- **icon.ico** - Windows application icon (256x256 or multi-size .ico file)

### macOS
- **icon.icns** - macOS application icon (512x512 or multi-size .icns file)

### Linux
- **icon.png** - Linux application icon (512x512 PNG file)

## Creating Icons

You can create these icons from a single source image (preferably 1024x1024 PNG):

### Online Tools
- [iConvert Icons](https://iconverticons.com/online/) - Convert PNG to ICO/ICNS
- [CloudConvert](https://cloudconvert.com/) - Multi-format converter

### Command Line Tools

**Windows (.ico):**
```bash
# Using ImageMagick
magick convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico
```

**macOS (.icns):**
```bash
# Using iconutil (macOS only)
mkdir icon.iconset
sips -z 16 16 icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32 icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32 icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64 icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128 icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256 icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256 icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512 icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512 icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset
```

**Linux (.png):**
```bash
# Just use a 512x512 PNG file
cp icon.png build/icon.png
```

## Temporary Placeholder

For development, you can use a simple placeholder icon. The build will work without icons, but the application will use default system icons.

## Icon Design Guidelines

- **Size:** Minimum 512x512, recommended 1024x1024
- **Format:** PNG with transparency
- **Style:** Simple, recognizable, works at small sizes
- **Colors:** Should work on both light and dark backgrounds
- **Content:** Represents API/HTTP/networking concept

## LocalAPI Icon Suggestions

Consider these concepts:
- API symbol (brackets, curly braces)
- HTTP/REST icon
- Network/connection symbol
- Thunder bolt (for speed)
- Gear/settings (for configuration)
- Combination of the above

Example: `{ API }` in a circle or hexagon shape
