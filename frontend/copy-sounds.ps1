# Скрипт для копирования звуковых файлов в public/sounds
if (Test-Path "sounds") {
    if (-not (Test-Path "public\sounds")) {
        New-Item -ItemType Directory -Path "public\sounds" -Force
    }
    Copy-Item -Path "sounds\*" -Destination "public\sounds\" -Force
    Write-Host "Звуковые файлы скопированы в public/sounds/"
} else {
    Write-Host "Папка sounds не найдена!"
}

