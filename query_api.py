#!/usr/bin/env python3
import json
import os
import re
from ctypes import ArgumentError

import spotipy
from jinja2 import Environment, FileSystemLoader, select_autoescape
from spotipy.oauth2 import SpotifyClientCredentials

# Die Alte und der Kommisar
# https://open.spotify.com/album/3snwe7XTiMOlxdRb97GZoq?si=U8UMUjW3Qu2LN_Z7_fPtdw

# Bibi und Tina
# https://open.spotify.com/playlist/25dIxWREnlY6a37FMj1sST?si=63bae965e44a48ff

# Lieselotte Postkuh - Alle Hoerspiele
# https://open.spotify.com/playlist/5SCbLiQEB8u5iWOHM9cNrn?si=2c19096064ad4f6c

# Die drei ??? Kids
# https://open.spotify.com/playlist/6GW1MH9yw8zA2AHDPW73cO?si=eda1239c13d84594

# not the best way - ToDo improve the error handling
try:
    if not os.environ['SPOTIPY_CLIENT_ID'] or os.environ['SPOTIPY_CLIENT_SECRET'] or os.environ['SPOTIPY_REDIRECT_URI']:
        pass
except KeyError:
    raise ArgumentError('Missing Environment Variables: SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI')

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

# get a list of albums
# extract title, id, cover from every item
# apply template


def get_type_and_if_from_url(url):
    """ extract the id for playlist or album from url
    """
    pattern = r'.*spotify.com\/([a-z]+)\/([a-zA-Z0-9]+)\?.*'
    _name, _id = re.match(pattern, url).groups()

    return {'type_name': _name, 'id': _id}

_type, _id = get_type_and_if_from_url('https://open.spotify.com/playlist/6GW1MH9yw8zA2AHDPW73cO?si=eda1239c13d84594').values()



_content = {}
if _type == 'playlist':
    query = spotify.playlist(playlist_id=_id)
    result = query['tracks']
    playlist_name = query['name']
    # while playlist_content['next']:
    all_tracks = result['items']
    while result['next']:
        result = spotify.next(result)
        all_tracks.extend(result['items'])

    for item in all_tracks:
        _content[item['track']['album']['id']] = item['track']['album']['name']
    

def get_openhab_relevant_data_from_album(album_ids):
    x = []
    if isinstance(album_ids, list):
        x.extend(album_ids)
    else:
        x.append(album_ids)
    _playlist = []
    for item in spotify.albums(x)['albums']:
        try:
            query = {}
            query["album_title"] = item['name']
            query["album_cover_tiny"] = item['images'][2]['url']
            query["album_cover_small"] = item['images'][1]['url']
            query["album_cover_large"] = item['images'][0]['url']
            query["album_id"] = item['id']

            _playlist.append(query)
        except (AttributeError, TypeError):
            continue
    return _playlist


playlist = []
album_ids = list(_content.keys())

for album_id in album_ids:
    playlist.extend(get_openhab_relevant_data_from_album(album_id))

templateLoader = FileSystemLoader(searchpath="./templates")
templateEnv = Environment(loader=templateLoader, autoescape=select_autoescape(['html', 'xml']))
TEMPLATE_FILE = "playlist.jinja2"
template = templateEnv.get_template(TEMPLATE_FILE)
outputText = template.render(playlist=playlist)


def create_widget_file(content:str, playlist_name:str, destination:str = '.') -> None:
    """ create appropriate widget file from given data to import in openhab
    """
    if not os.path.exists(destination):
        os.chdir(os.path.join(os.path.curdir,destination))
    else:
        os.chdir(destination)

    openhab_widget = {}
    openhab_widget['template'] = content
    openhab_widget['id'] = playlist_name
    openhab_widget['settings'] = ''

    target_filename = playlist_name.replace(" ", "_").lower()

    with open(f'{target_filename}.widget.json', 'w') as widget:
        widget.write(json.dumps(openhab_widget))



create_widget_file(outputText, playlist_name, 'output')
