@echo off
REM Run All Tests - Comprehensive Test Suite
REM Runs all test scripts in the project
REM Version: 2.1.0

setlocal enabledelayedexpansion

echo ============================================================
echo AI Coding Assistant - Complete Test Suite
echo Version: 2.1.0
echo ============================================================
echo.

set FAILED_TESTS=0
set PASSED_TESTS=0
set TOTAL_TESTS=0

REM Store start time
set START_TIME=%TIME%

echo Starting test execution at %START_TIME%
echo.
echo ============================================================

REM Test 1: Core Tests
echo.
echo [1/7] Running Core Tests...
echo ============================================================
if exist "scripts\run_tests.bat" (
    call scripts\run_tests.bat
    set TEST_RESULT=!ERRORLEVEL!
    if !TEST_RESULT! EQU 0 (
        echo [PASS] Core Tests
        set /a PASSED_TESTS+=1
    ) else (
        echo [FAIL] Core Tests
        set /a FAILED_TESTS+=1
    )
    set /a TOTAL_TESTS+=1
) else (
    echo [SKIP] Core Tests - script not found
)

REM Test 2: RAG Tests
echo.
echo [2/7] Running RAG Tests...
echo ============================================================
if exist "tests\test_rag.py" (
    python tests\test_rag.py
    set TEST_RESULT=!ERRORLEVEL!
    if !TEST_RESULT! EQU 0 (
        echo [PASS] RAG Tests
        set /a PASSED_TESTS+=1
    ) else (
        echo [FAIL] RAG Tests
        set /a FAILED_TESTS+=1
    )
    set /a TOTAL_TESTS+=1
) else (
    echo [SKIP] RAG Tests - test file not found
)

REM Test 3: Advanced RAG Tests
echo.
echo [3/7] Running Advanced RAG Tests...
echo ============================================================
if exist "tests\test_rag_advanced.py" (
    python tests\test_rag_advanced.py
    set TEST_RESULT=!ERRORLEVEL!
    if !TEST_RESULT! EQU 0 (
        echo [PASS] Advanced RAG Tests
        set /a PASSED_TESTS+=1
    ) else (
        echo [FAIL] Advanced RAG Tests
        set /a FAILED_TESTS+=1
    )
    set /a TOTAL_TESTS+=1
) else (
    echo [SKIP] Advanced RAG Tests - test file not found
)

REM Test 4: Phase 9.2 Tests
echo.
echo [4/7] Running Phase 9.2 Tests...
echo ============================================================
if exist "tests\test_phase_92.py" (
    python tests\test_phase_92.py
    set TEST_RESULT=!ERRORLEVEL!
    if !TEST_RESULT! EQU 0 (
        echo [PASS] Phase 9.2 Tests
        set /a PASSED_TESTS+=1
    ) else (
        echo [FAIL] Phase 9.2 Tests
        set /a FAILED_TESTS+=1
    )
    set /a TOTAL_TESTS+=1
) else (
    echo [SKIP] Phase 9.2 Tests - test file not found
)

REM Test 5: Phase 9.3 Tests
echo.
echo [5/7] Running Phase 9.3 Tests...
echo ============================================================
if exist "tests\test_phase_93.py" (
    python tests\test_phase_93.py
    set TEST_RESULT=!ERRORLEVEL!
    if !TEST_RESULT! EQU 0 (
        echo [PASS] Phase 9.3 Tests
        set /a PASSED_TESTS+=1
    ) else (
        echo [FAIL] Phase 9.3 Tests
        set /a FAILED_TESTS+=1
    )
    set /a TOTAL_TESTS+=1
) else (
    echo [SKIP] Phase 9.3 Tests - test file not found
)

REM Test 6: Project Lifecycle Tests
echo.
echo [6/7] Running Project Lifecycle Tests...
echo ============================================================
if exist "tests\test_templates.py" (
    pytest tests\test_templates.py -v
    set TEST_RESULT=!ERRORLEVEL!
    if !TEST_RESULT! EQU 0 (
        echo [PASS] Project Lifecycle Tests
        set /a PASSED_TESTS+=1
    ) else (
        echo [FAIL] Project Lifecycle Tests
        set /a FAILED_TESTS+=1
    )
    set /a TOTAL_TESTS+=1
) else (
    echo [SKIP] Project Lifecycle Tests - test file not found
)

REM Test 7: Automated Testing Tests (Phase 11.1)
echo.
echo [7/7] Running Automated Testing Tests (Phase 11.1)...
echo ============================================================
if exist "tests\test_automated_testing.py" (
    python tests\test_automated_testing.py
    set TEST_RESULT=!ERRORLEVEL!
    if !TEST_RESULT! EQU 0 (
        echo [PASS] Automated Testing Tests
        set /a PASSED_TESTS+=1
    ) else (
        echo [FAIL] Automated Testing Tests
        set /a FAILED_TESTS+=1
    )
    set /a TOTAL_TESTS+=1
) else (
    echo [SKIP] Automated Testing Tests - test file not found
)

REM Calculate end time and duration
set END_TIME=%TIME%

echo.
echo ============================================================
echo Test Execution Complete
echo ============================================================
echo.
echo Start Time: %START_TIME%
echo End Time:   %END_TIME%
echo.
echo ============================================================
echo Test Summary
echo ============================================================
echo Total Test Suites: %TOTAL_TESTS%
echo Passed:            %PASSED_TESTS%
echo Failed:            %FAILED_TESTS%
echo.

REM Display result
if %FAILED_TESTS% EQU 0 (
    echo Result: ALL TESTS PASSED!
    echo Status: SUCCESS
    echo.
    echo ============================================================
    echo.
    exit /b 0
) else (
    echo Result: SOME TESTS FAILED
    echo Status: FAILURE
    echo.
    echo Please review the failed tests above.
    echo ============================================================
    echo.
    exit /b 1
)
