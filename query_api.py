#!/usr/bin/env python3
import os
from ctypes import ArgumentError

import spotipy
from jinja2 import Environment, FileSystemLoader, select_autoescape
from spotipy.oauth2 import SpotifyClientCredentials

from api_tools.api_modules import (create_widget_file,
                                   get_playlist_from_spotify_playlist_url,
                                   load_query_information)

# not the best way - ToDo improve the error handling
try:
    if not os.environ['SPOTIPY_CLIENT_ID'] or os.environ['SPOTIPY_CLIENT_SECRET'] or os.environ['SPOTIPY_REDIRECT_URI']:
        pass
except KeyError:
    raise ArgumentError('Missing Environment Variables: SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI')

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

if __name__ == '__main__':
    """ run this script as standalone and create widget.json file """

    for item in load_query_information():
        print(f"{item['display_name']} - {item['playlist_url']}")

        playlist = get_playlist_from_spotify_playlist_url(spotify, item['playlist_url'])

        templateLoader = FileSystemLoader(searchpath="./templates")
        templateEnv = Environment(loader=templateLoader, autoescape=select_autoescape(['html', 'xml']))
        TEMPLATE_FILE = "playlist.jinja2"
        template = templateEnv.get_template(TEMPLATE_FILE)
        outputText = template.render(playlist=playlist)

        create_widget_file(outputText, item['display_name'], 'output')
