# Test Fixes Required

**Date:** October 24, 2025  
**Status:** 🔧 Fixing test errors

---

## 📋 Summary of Issues

### 1. Missing Dependencies
**Status:** ✅ FIXED in package.json
- Added `@testing-library/react`
- Added `@testing-library/jest-dom`
- Added `@testing-library/user-event`
- Added `jest-environment-jsdom`

**Action Required:** Run `npm install`

### 2. TabManagerService.test.ts - Multiple API Mismatches

**Issue:** Test was written against assumed API, actual API differs

**Required Changes:**
1. **Add `content` property** to all createTab calls (required field)
2. **Fix property names:** `lastAccessed` → `lastAccessedAt`
3. **Fix type values:** `'wsdl'` → `'other'` (not a valid type)
4. **Remove non-existent methods:** `pinTab`, `unpinTab`, `closeTabs`
5. **Remove persistence tests** (no file persistence in actual implementation)

### 3. RecentItems.test.tsx - Type Errors

**Issue:** Missing type annotations

**Required Changes:**
1. Add types to callback parameters
2. Ensure all imports are correct after npm install

---

## 🔧 Quick Fix Strategy

### Option 1: Simplified Tests (Recommended for Speed)
**Remove complex tests that don't match actual API**
- Keep basic CRUD tests
- Remove pin/unpin tests (API doesn't have these)
- Remove persistence tests (not in actual implementation)
- Simplify to match what TabManagerService actually provides

### Option 2: Match Actual API (Recommended for Quality)
**Update tests to match actual TabManagerService methods**

Check actual TabManagerService API:
```typescript
// Check src/main/services/TabManagerService.ts for:
- Available methods
- Required fields in Tab interface
- Actual property names
```

### Option 3: Start Fresh (Fastest)
**Write new minimal tests from scratch**
- 10-15 tests covering core functionality
- Based on actual API inspection
- No assumptions

---

## ✅ What I Recommend

**Immediate Actions:**

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Either:**
   
   **A. Let me write corrected, minimal test files** (20 min)
   - I'll inspect actual APIs
   - Write tests that match reality
   - Keep it simple and correct
   
   **B. Skip problematic tests for now** (5 min)
   - Focus on build success
   - Test manually
   - Add proper tests later
   
   **C. You fix the tests** (60 min)
   - I provide detailed fix instructions
   - You make the changes
   - We verify together

---

## 📊 Current Status

### Working ✅
- Build system (0 errors)
- Package.json updated with test dependencies
- Testing strategy documented
- Test structure planned

### Broken 🔧
- TabManagerService.test.ts (40+ type errors)
- RecentItems.test.tsx (20+ type errors)
- KeyboardShortcutManager.test.ts (may have issues)

### Not Started 📋
- 29 other test files

---

## 💡 My Recommendation

**Skip the broken tests for now and focus on build + manual testing:**

1. ✅ Build is working (verified)
2. ✅ All features compile
3. 🔧 Install test dependencies: `npm install`
4. ⏭️ Skip unit tests for now
5. ✅ Do manual testing of features
6. 📋 Come back to tests later with proper API inspection

**OR**

**Let me write 3-5 minimal, correct test files:**
- CommandPaletteService.test.ts (simple, no complex mocking)
- FavoritesService.test.ts (simple CRUD)
- CollapsibleSection.test.tsx (simple React component)
- These will work without errors
- Good examples for writing more tests later

---

## 🎯 Decision Time

**What would you like me to do?**

**A.** Install dependencies, then let me write 3-5 simple, WORKING test files
- Focus on quality over quantity
- Tests that actually run without errors
- Good templates for future tests

**B.** Provide detailed instructions for fixing TabManagerService.test.ts
- You make the fixes
- More learning for you
- Takes longer

**C.** Skip testing for now
- Install dependencies only
- Focus on manual testing
- Come back to automated tests later

**D.** Something else?

---

## 📞 Next Command

**If you choose Option A:**
```
"Write 3-5 simple, working test files"
```

**If you choose Option B:**
```
"Provide fix instructions for TabManagerService.test.ts"
```

**If you choose Option C:**
```
"Skip tests, install dependencies only"
```

---

**Current Status:** Waiting for direction on testing approach
