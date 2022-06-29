#FROM python:3.7-alpine
FROM python:3-alpine3.13

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step.
RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
            g++ \
            gcc \
            make \
            libc-dev \
            musl-dev \
            linux-headers \
            pcre-dev \
            postgresql-dev \
	        libxml2-dev \
	        libxslt-dev \
            mariadb-dev \
            libffi-dev \
	        jpeg-dev \
	        freetype-dev \
            git \
            python3-dev \
            sqlite-dev \
    && python3 -m venv /venv \
    && /venv/bin/pip install -U pip \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "/venv/bin/pip install --no-cache-dir wheel uwsgi tesla-ce mysqlclient psycopg2 cffi --upgrade" \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive /venv \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk del .build-deps

# Install production dependencies
RUN set -ex \
    && apk add --no-cache \
            postgresql-client \
            bash \
            vim \
            gcc \
            libressl-dev \
            freetype \
            jpeg \
            libxml2 \
            libxslt \
            nginx \
            supervisor \
            uwsgi \
            uwsgi-python3 \
            mariadb-connector-c \
            sqlite

# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
RUN mkdir /tesla/
WORKDIR /tesla/

# Install requirements
ADD requirements.txt requirements.txt
RUN /venv/bin/pip install -r requirements.txt

# Copy and prepare the entrypoint script for front-end
ADD docker/docker-entrypoint.sh /bin
RUN dos2unix /bin/docker-entrypoint.sh && chmod +x /bin/docker-entrypoint.sh

# uWSGI will listen on this port
EXPOSE 5000

# Add any custom, static environment variables needed by Django or your settings file here:
ENV DJANGO_SETTINGS_MODULE=tesla_ce_supervisor.settings

# Copy the code
ADD src/tesla_ce_supervisor /tesla/tesla_ce_supervisor
RUN cp /tesla/tesla_ce_supervisor/manage.py /tesla/manage.py

# Create a user and group for uWSGI and Celery
RUN addgroup -g 2000 -S web_group && \
    adduser -u 1000 -S web_user -G web_group

# Give permisions to root folder for this user
RUN chown -R web_user:web_group /tesla

# Copy the Nginx global conf
COPY docker/nginx.conf /etc/nginx/
# Copy the Flask Nginx site conf
COPY docker/django-site-nginx.conf /etc/nginx/conf.d/
# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
COPY docker/uwsgi.ini /etc/uwsgi/
# Custom Supervisord config
COPY docker/supervisord.conf /etc/supervisord.conf

# Generate static files
ENV STATICS_PATH=/tesla/static
RUN /venv/bin/python manage.py collectstatic --noinput

CMD ["/usr/bin/supervisord"]
ENTRYPOINT ["docker-entrypoint.sh"]
