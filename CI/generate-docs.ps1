# Базова директорія
$BASE_DIR = "C:\Users\user\Desktop\lab4"
$CI_DIR = "$BASE_DIR\CI"
$DEPLOY_DIR = "$CI_DIR\deploy"
$DOCS_DIR = "$DEPLOY_DIR\docs"
$HTML_DIR = "$DOCS_DIR\html"

# Шляхи до файлів
$INPUT_FILES = @(
    "C:\Users\user\Desktop\lab4\Client-side\main.py",
    "C:\Users\user\Desktop\lab4\Server-side\Server-side.ino"
)

$DOXYFILE_PATH = "$BASE_DIR\Doxyfile"

# Функція для перевірки та встановлення Doxygen
function Check-And-Install-Doxygen {
    if (-not (Get-Command doxygen -ErrorAction SilentlyContinue)) {
        Write-Host "Doxygen is not installed. Installing..."
        if (Get-Command brew -ErrorAction SilentlyContinue) {
            brew install doxygen
            if ($?) {
                Write-Host "Doxygen installed successfully."
            } else {
                Write-Host "Error: Failed to install Doxygen. Please install it manually."
                exit 1
            }
        } else {
            Write-Host "Error: Homebrew is not installed. Please install Homebrew and try again."
            exit 1
        }
    } else {
        Write-Host "Doxygen is already installed."
    }
}

# Перевірка та встановлення Doxygen
Check-And-Install-Doxygen

# Видалення старих результатів
Write-Host "Cleaning up old documentation..."
if (Test-Path $DOCS_DIR) {
    Write-Host "Removing $DOCS_DIR..."
    Remove-Item -Recurse -Force $DOCS_DIR
}

# Видалення старого Doxyfile
if (Test-Path $DOXYFILE_PATH) {
    Write-Host "Removing $DOXYFILE_PATH..."
    Remove-Item -Force $DOXYFILE_PATH
}

# Створення директорії для документації
Write-Host "Creating directories..."
New-Item -ItemType Directory -Force -Path $HTML_DIR

# Генерація Doxyfile
Write-Host "Generating Doxyfile in $BASE_DIR..."
doxygen -g $DOXYFILE_PATH

# Налаштування Doxyfile
Write-Host "Configuring Doxyfile..."
(Get-Content $DOXYFILE_PATH) | ForEach-Object {
    $_ -replace 'OUTPUT_DIRECTORY .*', "OUTPUT_DIRECTORY = $DOCS_DIR"  # Вказуємо директорію для результатів документації
    $_ -replace 'INPUT .*', "INPUT = $($INPUT_FILES -join ' ')"  # Вказуємо шляхи до вхідних файлів
    $_ -replace 'GENERATE_LATEX .*', 'GENERATE_LATEX = NO'  # Вимикаємо генерацію LaTeX
    $_ -replace 'RECURSIVE .*', 'RECURSIVE = YES'  # Використовуємо рекурсію для пошуку файлів
    $_ -replace 'EXTENSION_MAPPING .*', 'EXTENSION_MAPPING = ino=C++ py=Python'  # Вказуємо правильні мапінги
    $_ -replace 'FILE_PATTERNS .*', 'FILE_PATTERNS = *.ino *.cpp *.h *.py'  # Вказуємо шаблони для файлів
    $_ -replace 'GENERATE_HTML .*', 'GENERATE_HTML = YES'  # Увімкнути генерацію HTML
} | Set-Content $DOXYFILE_PATH

# Додаткові налаштування для кращої документації
Write-Host "Adding additional Doxygen configuration..."
Add-Content $DOXYFILE_PATH -Value "EXTRACT_ALL = YES"
Add-Content $DOXYFILE_PATH -Value "EXTRACT_PRIVATE = YES"
Add-Content $DOXYFILE_PATH -Value "SHOW_USED_FILES = YES"
Add-Content $DOXYFILE_PATH -Value "GENERATE_TREEVIEW = YES"
Add-Content $DOXYFILE_PATH -Value "DISABLE_INDEX = NO"

# Додавання груп для клієнта і сервера
Write-Host "Adding custom Doxygen groups for Client and Server..."
Add-Content $DOXYFILE_PATH -Value "
/**
 * @defgroup client_side Client Side
 * @brief Клієнтська частина гри Хрестики-нулики
 */"
Add-Content $DOXYFILE_PATH -Value "
/**
 * @defgroup server_side Server Side
 * @brief Серверна частина гри Хрестики-нулики
 */"

# Перевірка наявності вхідних файлів
Write-Host "Checking input files..."
foreach ($file in $INPUT_FILES) {
    if (-not (Test-Path $file)) {
        Write-Host "Error: Input file $file does not exist."
        exit 1
    }
}

# Генерація документації
Write-Host "Generating documentation..."
doxygen $DOXYFILE_PATH
if ($?) {
    Write-Host "Documentation generated successfully."
} else {
    Write-Host "Error: Documentation generation failed. Check $DOXYFILE_PATH for issues."
    exit 1
}

# Перевірка створення index.html
if (-not (Test-Path "$HTML_DIR\index.html")) {
    Write-Host "Error: index.html was not generated."
    exit 1
}

Write-Host "Documentation generated successfully. Open $HTML_DIR\index.html in your browser."