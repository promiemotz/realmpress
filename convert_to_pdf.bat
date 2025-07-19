@echo off
echo === Markdown to PDF Converter ===
echo Using Pandoc with wkhtmltopdf engine
echo.

REM Check if worldbook.md exists
if not exist "worldbook.md" (
    echo Error: worldbook.md not found in current directory
    pause
    exit /b 1
)

REM Check if Pandoc is installed
pandoc --version >nul 2>&1
if errorlevel 1 (
    echo Error: Pandoc is not installed or not in PATH
    echo Install with: choco install pandoc
    pause
    exit /b 1
)

REM Check if wkhtmltopdf is installed
wkhtmltopdf --version >nul 2>&1
if errorlevel 1 (
    echo Error: wkhtmltopdf is not installed or not in PATH
    echo Install with: choco install wkhtmltopdf
    pause
    exit /b 1
)

echo Converting worldbook.md to worldbook.pdf...
echo.

REM Convert using Pandoc with wkhtmltopdf
pandoc worldbook.md -o worldbook.pdf --pdf-engine=wkhtmltopdf --toc --number-sections --metadata title="Worldbook" --metadata author="Kanka Export"

if errorlevel 1 (
    echo.
    echo Error: Conversion failed
    pause
    exit /b 1
) else (
    echo.
    echo Successfully converted to worldbook.pdf
    
    REM Show file size if it exists
    if exist "worldbook.pdf" (
        for %%A in (worldbook.pdf) do (
            set /a size=%%~zA/1024/1024
            echo File size: !size! MB
        )
    )
    echo.
    echo Conversion completed successfully!
)

pause 