#---------------------------------CONFIGURABLE VARIABLES---------------------------------
$projectDir = "C:\Users\user\Desktop\lab5"
$testDir = "$projectDir\Client-side\tests"  # Шлях до директорії з тестами
$resultsDir = "$projectDir\lab5\deploy\test-results"  # Шлях до директорії для результатів тестів
$coverageDir = "$resultsDir\coverage_html_report"  # Шлях до директорії для звіту покриття
$venvDir = "$projectDir\venv"  # Шлях до віртуального середовища

# Параметри командного рядка
$COM_PORT = $args[0]
$BAUD_RATE = $args[1]

# Перевірка наявності порту та швидкості
if (-not $COM_PORT -or -not $BAUD_RATE) {
    Write-Output "Usage: $0 <COM_PORT> <BAUD_RATE>"
    exit 1
}

# Очистка старих результатів
Write-Output "Cleaning up old test results..."
Remove-Item -Recurse -Force $resultsDir
New-Item -ItemType Directory -Path $resultsDir | Out-Null

# Перевірка наявності Python
$pythonPath = (Get-Command "python" -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) {
    Write-Output "Python is not installed or not in PATH. Please install Python."
    exit 1
}

Write-Output "Using Python at $pythonPath"

# Створення віртуального середовища, якщо воно ще не створене
if (-not (Test-Path $venvDir)) {
    Write-Output "Creating virtual environment..."
    python -m venv $venvDir
}

# Активація віртуального середовища
Write-Output "Activating virtual environment..."
$activateScript = "$venvDir\Scripts\Activate.ps1"
& $activateScript

# Перевірка та встановлення залежностей у віртуальному середовищі
pip install --upgrade pip
$requiredPackages = @("coverage", "pytest", "pytest-cov", "pyserial")
foreach ($package in $requiredPackages) {
    if (-not (pip show $package)) {
        Write-Output "Installing $package..."
        pip install $package
    }
}

# Додати TEST_DIR до PYTHONPATH
$env:PYTHONPATH = "$testDir;$env:PYTHONPATH"

# Запуск програмних тестів із покриттям
Write-Output "Running software tests with coverage..."
coverage run -m pytest "$testDir\sw-tests.py" --junitxml="$resultsDir\sw-results.xml"

# Запуск апаратних тестів із покриттям
Write-Output "Running hardware tests with coverage..."
coverage run --append "$testDir\hw-tests.py" --port $COM_PORT --baudrate $BAUD_RATE

# Комбінування звітів покриття
Write-Output "Generating overall coverage report..."
coverage combine
coverage report > "$resultsDir\coverage.txt"
coverage html -d "$coverageDir"

# Деактивація віртуального середовища
deactivate

# Виведення результатів
Write-Output "Tests completed. Results are saved in $resultsDir"
Write-Output "Coverage report available at $coverageDir\index.html"
