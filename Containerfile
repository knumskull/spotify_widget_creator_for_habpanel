FROM registry.access.redhat.com/ubi9/python-39
LABEL org.opencontainers.image.authors="steffen@froemer.net"
LABEL maintainer="Steffen Froemer <steffen@froemer.net>"
LABEL description=""

ARG SPOTIPY_CLIENT_ID
ARG SPOTIPY_CLIENT_SECRET
ARG SPOTIPY_REDIRECT_URI

RUN pip install -U pip
RUN git clone https://github.com/knumskull/spotify_widget_creator_for_habpanel.git ${APP_ROOT}/app
RUN pip install -r ${APP_ROOT}/app/requirements.txt

WORKDIR ${APP_ROOT}/app
CMD python3 ${APP_ROOT}/app/query_api.py

