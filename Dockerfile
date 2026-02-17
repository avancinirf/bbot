FROM php:8.4-apache

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        git \
        unzip \
        ca-certificates \
        pkg-config \
        sqlite3 \
        libsqlite3-dev \
        libzip-dev \
        libonig-dev \
        libxml2-dev \
        libcurl4-openssl-dev \
    ; \
    docker-php-ext-install -j"$(nproc)" \
        pdo_sqlite \
        mbstring \
        xml \
        dom \
        zip \
        curl \
    ; \
    a2enmod rewrite headers; \
    rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 /usr/bin/composer /usr/local/bin/composer

COPY docker/apache/000-default.conf /etc/apache2/sites-available/000-default.conf
COPY docker/apache/servername.conf /etc/apache2/conf-available/servername.conf
RUN a2enconf servername

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

WORKDIR /var/www/html

ENTRYPOINT ["entrypoint.sh"]
CMD ["apache2-foreground"]
