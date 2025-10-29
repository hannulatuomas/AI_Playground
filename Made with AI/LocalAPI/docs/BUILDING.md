# Building LocalAPI

**Version:** 0.7.0  
**Last Updated:** October 23, 2025

This guide covers building and packaging LocalAPI for distribution.

## Prerequisites

### All Platforms
- Node.js 18+ installed
- All dependencies installed (`npm install`)
- Application built (`npm run build`)

### Windows
- No additional requirements

### macOS
- Xcode Command Line Tools
- Apple Developer account (for code signing, optional)

### Linux
- Standard build tools (`build-essential`)

## Build Commands

### Development Build
```bash
# Build TypeScript and bundle React
npm run build
```

This creates:
- `dist/main/` - Compiled main process
- `dist/preload/` - Compiled preload script
- `dist/renderer/` - Bundled React app

### Package for Current Platform
```bash
# Package for your current OS
npm run package
```

### Package for Specific Platform

**Windows:**
```bash
npm run package:win
```
Creates:
- `LocalAPI-0.1.0-x64.exe` - NSIS installer
- `LocalAPI-0.1.0-portable.exe` - Portable version

**macOS:**
```bash
npm run package:mac
```
Creates:
- `LocalAPI-0.1.0-x64.dmg` - Intel Mac installer
- `LocalAPI-0.1.0-arm64.dmg` - Apple Silicon installer
- `LocalAPI-0.1.0-x64.zip` - Intel Mac archive
- `LocalAPI-0.1.0-arm64.zip` - Apple Silicon archive

**Linux:**
```bash
npm run package:linux
```
Creates:
- `LocalAPI-0.1.0-x64.AppImage` - Universal Linux app
- `LocalAPI-0.1.0-x64.deb` - Debian/Ubuntu package
- `LocalAPI-0.1.0-x64.rpm` - RedHat/Fedora package

### Package All Platforms
```bash
# Windows script
scripts\package-all.bat

# Or manually
npm run build
npm run package:win
npm run package:mac
npm run package:linux
```

## Build Configuration

### electron-builder.yml
Main configuration file for electron-builder. Defines:
- App metadata (name, ID, copyright)
- Build directories
- Platform-specific settings
- File inclusion/exclusion patterns

### package.json
Contains:
- Build scripts
- Dependencies
- Basic electron-builder config

## Icons

Icons must be placed in `build/` directory:

- **Windows:** `icon.ico` (256x256 or multi-size)
- **macOS:** `icon.icns` (512x512 or multi-size)
- **Linux:** `icon.png` (512x512)

See `build/README.md` for icon creation instructions.

## Output

All build artifacts are created in `release/` directory:

```
release/
├── LocalAPI-0.1.0-x64.exe          # Windows installer
├── LocalAPI-0.1.0-portable.exe     # Windows portable
├── LocalAPI-0.1.0-x64.dmg          # macOS Intel
├── LocalAPI-0.1.0-arm64.dmg        # macOS Apple Silicon
├── LocalAPI-0.1.0-x64.AppImage     # Linux universal
├── LocalAPI-0.1.0-x64.deb          # Linux Debian
└── LocalAPI-0.1.0-x64.rpm          # Linux RedHat
```

## Code Signing

### Windows
Optional. For production:
1. Obtain code signing certificate
2. Set environment variables:
   ```bash
   set CSC_LINK=path\to\certificate.pfx
   set CSC_KEY_PASSWORD=your_password
   ```
3. Build with signing:
   ```bash
   npm run package:win
   ```

### macOS
Optional. For production:
1. Join Apple Developer Program
2. Create certificates in Xcode
3. Set environment variables:
   ```bash
   export CSC_LINK=path/to/certificate.p12
   export CSC_KEY_PASSWORD=your_password
   export APPLE_ID=your@email.com
   export APPLE_ID_PASSWORD=app_specific_password
   ```
4. Build with signing:
   ```bash
   npm run package:mac
   ```

### Linux
No code signing required.

## Auto-Updates

To enable auto-updates:

1. Set up GitHub releases or other update server
2. Configure in `electron-builder.yml`:
   ```yaml
   publish:
     provider: github
     owner: your-username
     repo: localapi
   ```
3. Implement update checking in app

## Troubleshooting

### Build Fails
- Ensure all dependencies installed: `npm install`
- Clean build: `rm -rf dist node_modules && npm install`
- Check Node.js version: `node --version` (should be 18+)

### Missing Icons
- Build will work but use default icons
- Add proper icons to `build/` directory
- See `build/README.md` for instructions

### Native Modules Fail
- Rebuild native modules: `npm rebuild`
- Install platform build tools
- Check `better-sqlite3` is installed correctly

### Large Bundle Size
- electron-builder automatically excludes dev dependencies
- Check `files` pattern in `electron-builder.yml`
- Use `asar: true` for compression (already enabled)

### macOS Gatekeeper Issues
- App needs to be signed for distribution
- For development: Right-click → Open
- Or disable Gatekeeper temporarily (not recommended)

### Linux Dependencies
- Install required system libraries
- For Debian/Ubuntu:
  ```bash
  sudo apt-get install libgconf-2-4 libnotify4 libappindicator1
  ```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Build

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - run: npm install
      - run: npm run build
      - run: npm run package
      
      - uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.os }}-build
          path: release/*
```

## Distribution

### Windows
- Upload `.exe` installer to website/GitHub releases
- Users download and run installer
- Or use portable `.exe` for no-install usage

### macOS
- Upload `.dmg` files to website/GitHub releases
- Users download, open DMG, drag to Applications
- Or distribute `.zip` for command-line users

### Linux
- Upload `.AppImage` for universal compatibility
- Upload `.deb` for Debian/Ubuntu users
- Upload `.rpm` for RedHat/Fedora users
- Or publish to package repositories

## Release Checklist

- [ ] Update version in `package.json`
- [ ] Update `CHANGELOG.md`
- [ ] Run tests: `npm test`
- [ ] Build application: `npm run build`
- [ ] Package for all platforms
- [ ] Test installers on each platform
- [ ] Create GitHub release
- [ ] Upload build artifacts
- [ ] Update documentation
- [ ] Announce release

## Performance Tips

- Use `asar: true` for faster loading
- Exclude unnecessary files in `electron-builder.yml`
- Minimize dependencies
- Use code splitting in React
- Enable compression

## Security

- Never commit signing certificates
- Use environment variables for secrets
- Enable `hardenedRuntime` on macOS
- Set proper entitlements
- Keep dependencies updated

---

For more information, see:
- [electron-builder documentation](https://www.electron.build/)
- [Electron documentation](https://www.electronjs.org/docs)
