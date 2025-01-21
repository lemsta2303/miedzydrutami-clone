FROM prestashop/prestashop:1.7.8

RUN rm -rf /var/www/html
COPY ./prestashop /var/www/html
RUN chmod 777 -R /var/www/html
COPY ./backup /tmp/sql
RUN chmod 777 -R /tmp/sql

RUN apt-get update && apt-get install -y openssl

# Create directories for SSL keys and certificates
RUN mkdir -p /etc/ssl/ssl-certs

# Generate SSL key and certificate using a temporary configuration file
RUN printf "[dn]\nCN=localhost\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth" > /tmp/openssl.cnf \
    && openssl req -x509 -nodes -days 365 -newkey rsa:4096 -sha256 \
    -keyout /etc/ssl/ssl-certs/ssl-key.key \
    -out /etc/ssl/ssl-certs/ssl-certificate.crt \
    -subj "/C=PL/ST=Pomorskie/L=Gdansk/O=./OU=./CN=localhost" \
    -extensions EXT -config /tmp/openssl.cnf \
    && rm /tmp/openssl.cnf

# Set permissions for SSL certificates
RUN chown www-data:www-data /etc/ssl/ssl-certs/ssl-key.key /etc/ssl/ssl-certs/ssl-certificate.crt

# Copy SSL configuration
COPY ./config/ssl-certs.conf /etc/apache2/sites-available/ssl-certs.conf

# Enable SSL module and site configuration
RUN a2enmod ssl && a2ensite ssl-certs.conf

ENTRYPOINT ["/tmp/sql/restore_settings.sh"]

CMD ["apache2-foreground"]