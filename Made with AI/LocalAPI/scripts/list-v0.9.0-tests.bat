@echo off
echo ======================================
echo v0.9.0 Test Suite - File List
echo ======================================
echo.

echo SERVICE TESTS (5 files):
echo   1. tests\unit\services\TabManagerService.test.ts
echo   2. tests\unit\services\KeyboardShortcutManager.test.ts
echo   3. tests\unit\services\CommandPaletteService.test.ts
echo   4. tests\unit\services\FavoritesService.test.ts
echo   5. tests\unit\services\LayoutService.test.ts
echo.

echo COMPONENT TESTS (4 files):
echo   6. tests\unit\components\RecentItems.test.tsx
echo   7. tests\unit\components\CollapsibleSection.test.tsx
echo   8. tests\unit\components\BreadcrumbNavigation.test.tsx
echo   9. tests\unit\components\EnhancedTabBar.test.tsx
echo.

echo INTEGRATION TESTS (3 files):
echo   10. tests\integration\KeyboardShortcuts.integration.test.tsx
echo   11. tests\integration\TabManagement.integration.test.tsx
echo   12. tests\integration\SearchAndNavigation.integration.test.tsx
echo.

echo ======================================
echo TOTAL: 12 test files, 323+ test cases
echo ======================================
echo.

echo Run all tests: npm test
echo Run with coverage: npm test -- --coverage
echo.

pause
