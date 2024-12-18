# Перевірка вхідних параметрів
if ($args.Length -ne 2) {
    Write-Host "Usage: .\deploy.ps1 <COM Port> <Baud Rate>"
    exit 1
}

$COM_PORT = $args[0]
$BAUD_RATE = $args[1]

# Директориї
$CLIENT_DIR = "C:\Users\user\Desktop\lab3\Client-side"
$SERVER_DIR = "C:\Users\user\Desktop\lab3\Server-side"
$TEST_DIR = "$CLIENT_DIR"
$DEPLOY_DIR = "$CLIENT_DIR\deploy"

$CLIENT_OUTPUT_DIR = "$DEPLOY_DIR\client-output"
$SERVER_OUTPUT_DIR = "$DEPLOY_DIR\server-output"
$TEST_RESULTS_DIR = "$DEPLOY_DIR\test-results"
$VENV_DIR = "$CLIENT_DIR\.venv"  # Шлях до папки віртуального середовища

# Видалення тимчасових папок, якщо вони є (не видаляємо venv)
Write-Host "Cleaning up old directories..."
if (Test-Path $DEPLOY_DIR) {
    Write-Host "Removing deploy directory..."
    Remove-Item -Recurse -Force $DEPLOY_DIR
}

if (Test-Path "__pycache__") {
    Write-Host "Removing __pycache__..."
    Remove-Item -Recurse -Force "__pycache__"
}

# Видалення `test-result.json`, якщо він існує
if (Test-Path "result\test-result.json") {
    Write-Host "Removing test-result.json..."
    Remove-Item -Force "result\test-result.json"
}

# Переміщення `tiktaktoe.ini` до папки `$CLIENT_OUTPUT_DIR`
$tiktaktoePath = "$CLIENT_DIR\tiktaktoe.ini"
if (Test-Path $tiktaktoePath) {
    Write-Host "Moving tiktaktoe.ini to client-output directory..."
    Move-Item -Force $tiktaktoePath -Destination "$CLIENT_OUTPUT_DIR"
}

# Активуємо віртуальне середовище
$activateScript = "$VENV_DIR\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Host "Activating virtual environment..."
    & $activateScript
} else {
    Write-Host "Error: Activate.ps1 not found."
    exit 1
}

# Функція для встановлення залежностей Python
function install-python-dependencies {
    Write-Host "Installing dependencies..."
    python -m pip install --upgrade pip > $null
    pip install pyserial PyQt5 pytest pyinstaller > $null

    Write-Host "Python dependencies installed successfully."
}

# Встановлення Python залежностей
install-python-dependencies

# Створення директорій для артефактів
Write-Host "Creating necessary directories..."
New-Item -ItemType Directory -Force -Path $CLIENT_OUTPUT_DIR
New-Item -ItemType Directory -Force -Path $SERVER_OUTPUT_DIR
New-Item -ItemType Directory -Force -Path $TEST_RESULTS_DIR

# Білд клієнта (з генерацією виконуваного файлу)
Write-Host "Building client..."
pyinstaller --onefile "$CLIENT_DIR\main.py" --distpath "$CLIENT_OUTPUT_DIR"
if (-Not $?) {
    Write-Host "Client build failed. Check $CLIENT_OUTPUT_DIR for details."
    exit 1
} else {
    Write-Host "Client built successfully." -ForegroundColor Green
}

# Видалення папки build
if (Test-Path "$CLIENT_DIR\build") {
    Write-Host "Removing build directory..."
    Remove-Item -Recurse -Force "$CLIENT_DIR\build"
}

# Компіляція серверу
Write-Host "Compiling server firmware..."
& "Arduino-cli" compile --fqbn arduino:avr:uno "$SERVER_DIR\Server-side.ino" --output-dir $SERVER_OUTPUT_DIR
if (-Not $?) {
    Write-Host "Firmware compilation failed."
    exit 1
} else {
    Write-Host "Server firmware compiled successfully." -ForegroundColor Green
}

# Завантаження прошивки
Write-Host "Uploading firmware to the board..."
& "arduino-cli" upload -p $COM_PORT --fqbn arduino:avr:uno "$SERVER_DIR\Server-side.ino"
if (-Not $?) {
    Write-Host "Firmware upload failed."
    exit 1
}

# Запуск тестів (з генерацією звітів у форматі JUnit)
Write-Host "Running tests..."
pytest "$TEST_DIR\test.py" -v --capture=tee-sys --junitxml="$TEST_RESULTS_DIR\results.xml" > "$TEST_RESULTS_DIR\results.log" 2>&1
if (-Not $?) {
    Write-Host "Tests failed. Check $TEST_RESULTS_DIR\results.log for details."
    exit 1
}

# Завершення
Write-Host "Deployment completed successfully. Artifacts are in the $DEPLOY_DIR directory."
