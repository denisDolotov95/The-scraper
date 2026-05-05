FROM python:3.12-slim

# Переменные окрудения для ру сегмента
ENV LANG='ru_RU.UTF-8' \
    LANGUAGE='ru_RU:ru' \
    LC_ALL='ru_RU.UTF-8' \
    LC_MESSAGES='en_US.UTF-8' \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/Moscow

# Конфигурация локали и временной зоны
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    locales \
    tzdata && \
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && \
    echo "ru_RU.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen en_US.UTF-8 ru_RU.UTF-8 && \
    ln -fs /usr/share/zoneinfo/Europe/Moscow /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Место хранения исходных файлов
WORKDIR /usr/src

# Установка всех зависимостей для проекта
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
    
RUN playwright install chromium && \
    playwright install-deps chromium

# Copy application code
COPY . .

# Запуск проекта
ARG FILE_INN
ENV FILE_INN=$FILE_INN

# Copy application code
COPY . .
RUN chmod 755 entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python3", "app"]