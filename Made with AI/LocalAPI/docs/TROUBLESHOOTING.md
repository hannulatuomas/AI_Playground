# Troubleshooting Guide

**Version:** 0.7.0  
**Last Updated:** October 23, 2025

Common issues and solutions for LocalAPI.

---

## Native Module Errors

### Error: NODE_MODULE_VERSION mismatch

**Symptoms:**
```
Error: The module 'better-sqlite3' was compiled against a different Node.js version
NODE_MODULE_VERSION 127 vs NODE_MODULE_VERSION 119
```

**Cause:**
Native modules (like better-sqlite3) need to be compiled for the specific Electron version you're using.

**Solution 1 - Quick Fix:**
```bash
npm run fix:native
```

**Solution 2 - Manual Fix:**
```bash
npm rebuild better-sqlite3
npx electron-rebuild -f -w better-sqlite3
npm run build
```

**Solution 3 - Script:**
```bash
scripts\fix-native-modules.bat
```

**Prevention:**
After updating Electron or Node.js versions, always run:
```bash
npm run fix:native
```

---

## Database Errors

### Error: Database not initialized

**Symptoms:**
```
Error: Database not initialized
at DatabaseService.getAllCollections
```

**Cause:**
Database failed to initialize, usually due to native module issues.

**Solution:**
1. Fix native modules (see above)
2. Rebuild the application:
```bash
npm run build
npm run dev
```

3. If issue persists, delete the database and restart:
```bash
# Windows
del %APPDATA%\localapi\localapi.db
# macOS/Linux
rm ~/Library/Application\ Support/localapi/localapi.db
```

---

## Build Errors

### Error: Cannot find module

**Symptoms:**
```
Error: Cannot find module 'xyz'
```

**Solution:**
```bash
npm install
npm run build
```

### Error: TypeScript compilation failed

**Symptoms:**
```
error TS2304: Cannot find name 'xyz'
```

**Solution:**
1. Check TypeScript version:
```bash
npx tsc --version
```

2. Clean and rebuild:
```bash
npm run clean
npm install
npm run build
```

---

## Runtime Errors

### Error: Port already in use

**Symptoms:**
```
Error: listen EADDRINUSE: address already in use :::5173
```

**Solution:**
Kill the process using the port:

**Windows:**
```bash
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
lsof -ti:5173 | xargs kill -9
```

### Error: Electron failed to start

**Symptoms:**
Application window doesn't open or crashes immediately.

**Solution:**
1. Check console for errors
2. Rebuild native modules:
```bash
npm run fix:native
```
3. Clear Electron cache:
```bash
# Windows
rmdir /s /q %APPDATA%\localapi
# macOS
rm -rf ~/Library/Application\ Support/localapi
```

---

## Test Errors

### Error: Tests timing out

**Symptoms:**
```
Timeout - Async callback was not invoked within the 5000 ms timeout
```

**Solution:**
Increase test timeout in jest.config.js:
```javascript
testTimeout: 30000, // 30 seconds
```

### Error: Mock not working

**Symptoms:**
Tests making real HTTP requests or failing with network errors.

**Solution:**
Ensure axios is mocked in your test:
```javascript
jest.mock('axios');
const axios = require('axios');

beforeEach(() => {
  axios.mockResolvedValue({ status: 200, data: {} });
});
```

---

## Performance Issues

### Application is slow

**Symptoms:**
UI is laggy or unresponsive.

**Solutions:**

1. **Clear cache:**
```bash
# In app: Cache tab → Clear All Cache
```

2. **Check database size:**
```bash
# Windows
dir %APPDATA%\localapi\localapi.db
```

3. **Optimize database:**
```sql
VACUUM;
ANALYZE;
```

4. **Disable unnecessary features:**
- Disable caching if not needed
- Reduce cron monitor frequency
- Limit mock server logging

---

## Security Testing Issues

### OWASP scan fails

**Symptoms:**
OWASP scanner returns errors or no results.

**Solutions:**

1. **Check target URL is accessible:**
```bash
curl -I https://target-url.com
```

2. **Verify scan depth:**
- Use "quick" for fast scans
- Use "standard" for comprehensive scans
- Use "deep" only when necessary

3. **Check findings export:**
- Ensure write permissions
- Check disk space

### ZAP integration fails

**Symptoms:**
Cannot connect to ZAP proxy.

**Solutions:**

1. **Verify ZAP is running:**
- Start OWASP ZAP
- Check it's listening on correct port (default: 8080)

2. **Check API key:**
- Tools → Options → API
- Copy API key to LocalAPI

3. **Test connection:**
```bash
curl http://localhost:8080/JSON/core/view/version/?apikey=YOUR_KEY
```

---

## Installation Issues

### npm install fails

**Symptoms:**
```
npm ERR! code ELIFECYCLE
```

**Solutions:**

1. **Clear npm cache:**
```bash
npm cache clean --force
```

2. **Delete node_modules and reinstall:**
```bash
rmdir /s /q node_modules
del package-lock.json
npm install
```

3. **Use specific Node.js version:**
```bash
nvm use 18
npm install
```

---

## Development Issues

### Hot reload not working

**Symptoms:**
Changes not reflected in running application.

**Solutions:**

1. **Restart dev server:**
```bash
# Stop with Ctrl+C
npm run dev
```

2. **Clear Vite cache:**
```bash
rmdir /s /q node_modules\.vite
```

3. **Hard refresh browser:**
- Ctrl+Shift+R (Windows/Linux)
- Cmd+Shift+R (macOS)

---

## Common Questions

### Q: How do I reset the application?

**A:** Delete the application data folder:

**Windows:**
```bash
rmdir /s /q %APPDATA%\localapi
```

**macOS:**
```bash
rm -rf ~/Library/Application\ Support/localapi
```

**Linux:**
```bash
rm -rf ~/.config/localapi
```

### Q: How do I update dependencies?

**A:**
```bash
npm update
npm run fix:native
npm run build
```

### Q: How do I check logs?

**A:** Logs are in:
- **Windows:** `%APPDATA%\localapi\logs`
- **macOS:** `~/Library/Application Support/localapi/logs`
- **Linux:** `~/.config/localapi/logs`

### Q: How do I report a bug?

**A:** Open an issue on GitHub with:
1. Steps to reproduce
2. Expected vs actual behavior
3. Screenshots if applicable
4. Version number (Help → About)
5. Console logs

---

## Getting Help

### Resources

- **Documentation:** [docs/](../docs/)
- **User Guide:** [USER_GUIDE.md](USER_GUIDE.md)
- **Quick Start:** [QUICKSTART.md](QUICKSTART.md)
- **API Docs:** [API.md](API.md)

### Support Channels

- **GitHub Issues:** Report bugs and request features
- **Discussions:** Ask questions and share ideas
- **Documentation:** Check guides and tutorials

---

## Debug Mode

### Enable Debug Logging

Set environment variable:
```bash
# Windows
set DEBUG=localapi:*
npm run dev

# macOS/Linux
DEBUG=localapi:* npm run dev
```

### Electron DevTools

Press `F12` or `Ctrl+Shift+I` to open DevTools.

### Check Console

Look for errors in:
1. Main process console (terminal)
2. Renderer process console (DevTools)

---

## Still Having Issues?

1. ✅ Check this troubleshooting guide
2. ✅ Search existing GitHub issues
3. ✅ Check documentation
4. ✅ Enable debug mode
5. ✅ Open a new GitHub issue with details

---

**Last Updated:** October 23, 2025  
**Version:** 0.7.0
