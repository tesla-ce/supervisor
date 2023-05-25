FROM python:3-alpine
ENV SUPERVISOR_DATA '/data'
ENV PGDATA '/data/postgres/pgdata'
ENV POSTGRES_PASSWORD_FILE '/data/secrets/DB_ROOT_PASSWORD'

ENV POSTGRES_DB 'supervisor'
ENV POSTGRES_USER 'supervisor'
ENV GOSU_VERSION 1.16
ENV POSTGRES_HOST '127.0.0.1'
ENV POSTGRES_PORT '5432'

RUN mkdir -p $SUPERVISOR_DATA && mkdir -p $PGDATA && mkdir -p /data/secrets

RUN set -eux; \
	addgroup -g 70 -S postgres; \
	adduser -u 70 -S -D -G postgres -H -h $PGDATA -s /bin/sh postgres; \
	mkdir -p /var/lib/postgresql; \
	chown -R postgres:postgres $PGDATA

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
            zlib-dev \
    && python3 -m venv /venv \
    && /venv/bin/pip install -U pip \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "/venv/bin/pip install --no-cache-dir wheel uwsgi mysqlclient psycopg2 cffi pyminizip --upgrade" \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive /venv \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk del .build-deps

# postgres configuration
RUN set -eux; \
	\
	apk add --no-cache --virtual .gosu-deps \
		ca-certificates \
		dpkg \
		gnupg \
	; \
	\
	dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')"; \
	wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch"; \
	wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc"; \
	\
# verify the signature
	export GNUPGHOME="$(mktemp -d)"; \
	gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4; \
	gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu; \
	gpgconf --kill all; \
	rm -rf "$GNUPGHOME" /usr/local/bin/gosu.asc; \
	\
# clean up fetch dependencies
	apk del --no-network .gosu-deps; \
	\
	chmod +x /usr/local/bin/gosu

RUN mkdir /docker-entrypoint-initdb.d


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
            sqlite \
            postgresql

# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
RUN mkdir /tesla/
WORKDIR /tesla/

# Install requirements
ADD requirements.txt requirements.txt
RUN /venv/bin/pip install -r requirements.txt

# Copy and prepare the entrypoint script for front-end
ADD docker/docker-entrypoint.sh /bin
ADD docker/postgres_docker-entrypoint.sh /bin
ADD docker/wait_for_it.sh /bin
RUN dos2unix /bin/docker-entrypoint.sh && chmod +x /bin/docker-entrypoint.sh
RUN dos2unix /bin/postgres_docker-entrypoint.sh && chmod +x /bin/postgres_docker-entrypoint.sh
RUN dos2unix /bin/wait_for_it.sh && chmod +x /bin/wait_for_it.sh




# uWSGI will listen on this port
EXPOSE 5000

# Add any custom, static environment variables needed by Django or your settings file here:
ENV DJANGO_SETTINGS_MODULE=tesla_ce_supervisor.settings

# Copy the code
ADD src/tesla_ce_supervisor /tesla/tesla_ce_supervisor
RUN cp /tesla/tesla_ce_supervisor/manage.py /tesla/manage.py

# Create a user and group for uWSGI and Celery
RUN addgroup -g 2000 -S web_group && addgroup -S docker && \
    adduser -u 1000 -S web_user -G web_group docker

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

# USER web_user
# Generate static files
ENV STATICS_PATH=/tesla/static
RUN SETUP_MODE=BUILD /venv/bin/python manage.py collectstatic --noinput

STOPSIGNAL SIGINT

CMD ["/usr/bin/supervisord"]
ENTRYPOINT ["docker-entrypoint.sh"]
