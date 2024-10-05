#!/bin/bash

# Переменные окружения
CONFIG_FILE="config.env"
PYTHON_VERSION="python3"
VENV_DIR="Cula"
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/bot.log"

# Создание виртуального окружения
echo ">>> Устанавливаем Python и создаем виртуальное окружение..."
sudo apt update
sudo apt install -y $PYTHON_VERSION $PYTHON_VERSION-venv

# Создаем виртуальное окружение, если оно еще не существует
if [ ! -d "$VENV_DIR" ]; then
    $PYTHON_VERSION -m venv $VENV_DIR
    echo ">>> Виртуальное окружение создано."
else
    echo ">>> Виртуальное окружение уже существует."
fi

# Активируем виртуальное окружение
source $VENV_DIR/bin/activate

# Установка зависимостей
echo ">>> Устанавливаем зависимости..."
pip install -r requirements.txt

# Создание директории для логов, если она не существует
if [ ! -d "$LOG_DIR" ]; then
    mkdir $LOG_DIR
    echo ">>> Директория для логов создана."
else
    echo ">>> Директория для логов уже существует."
fi

# Чтение конфигурации из файла .env
echo ">>> Чтение параметров из конфигурационного файла $CONFIG_FILE..."
source $CONFIG_FILE

# Настройка cron для регулярного выполнения задачи
CRON_INTERVAL=${CRON_INTERVAL:-"0 * * * *"}  # Интервал по умолчанию: каждый час
CRON_COMMAND="cd $(pwd) && $VENV_DIR/bin/python main.py >> $(pwd)/$LOG_FILE 2>&1"

# Проверка на существование cron задачи и добавление её, если нет
(crontab -l | grep -F "$CRON_COMMAND") || (echo "$CRON_INTERVAL $CRON_COMMAND" | crontab -)

echo ">>> Cron задача настроена на выполнение каждые $CRON_INTERVAL."
echo ">>> Установка завершена."
