#!/usr/bin/env python3
import json
import os
import re
from ctypes import ArgumentError

import requests
import spotipy
from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image
from requests.adapters import HTTPAdapter
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from urllib3.util.retry import Retry
from yaml import FullLoader, load as yaml_load
from api_tools.api_modules import get_playlist_from_spotify_playlist_url


# not the best way - ToDo improve the error handling
try:
    if not os.environ['SPOTIPY_CLIENT_ID'] or os.environ['SPOTIPY_CLIENT_SECRET'] or os.environ['SPOTIPY_REDIRECT_URI']:
        pass
except KeyError:
    raise ArgumentError('Missing Environment Variables: SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI')


# https://developer.spotify.com/documentation/general/guides/authorization/scopes/
scope = ' playlist-modify-public'
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))



if __name__ == '__main__':
    """ run this script as standalone and create widget.json file """
    print(os.environ)
    # playlist = get_playlist_from_spotify_playlist_url(spotify, )

    url = 'https://open.spotify.com/playlist/3sY0G7W8WjEMTL496OF982'

    pattern = r'.*spotify.com\/([a-z]+)\/([a-zA-Z0-9]+)\??.*'
    _type, _id = re.match(pattern, url).groups()

    items = spotify.playlist_items(_id)

    list_of_item_ids = []
    for item in items['items']:
        list_of_item_ids.append(item['track']['id'])
    # list_of_item_ids = ['7cOn1MAUPVr1ZKr7zBOM9s']

    print(list_of_item_ids)

    a = spotify.playlist_remove_all_occurrences_of_items(_id, list_of_item_ids)
