#!/usr/bin/env python3
import json
import os
import re

import requests
from PIL import Image
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from yaml import FullLoader
from yaml import load as yaml_load


def load_query_information() -> dict:
    """ load information to query from YAML file and provide as list """
    try:
        with open('query_data.yaml') as f:
            data = yaml_load(f, Loader=FullLoader)
    except FileNotFoundError as err:
        print(f"File 'query_data.yml' not found. ({err})")
        
    return data

def query_spotify_api(client, url) -> dict:
    """ Based on given url, query relevant information from Spotify API """

    pattern = r'.*spotify.com\/([a-z]+)\/([a-zA-Z0-9]+)\??.*'
    _type, _id = re.match(pattern, url).groups()

    _content = {}
    if _type == 'playlist':
        query = client.playlist(playlist_id=_id)
        result = query['tracks']
        playlist_name = query['name']
        all_tracks = result['items']
        while result['next']:
            result = client.next(result)
            all_tracks.extend(result['items'])

        for item in all_tracks:
            _content[item['track']['album']['id']] = item['track']['album']['name']

    return _content

def get_openhab_relevant_data_from_album(spotify_client, album_ids) -> list:
    """ """
    x = []
    if isinstance(album_ids, list):
        x.extend(album_ids)
    else:
        x.append(album_ids)
    _playlist = []

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    for item in spotify_client.albums(x)['albums']:
        try:
            query = {}
            query["album_title"] = item['name']
            query["album_cover_tiny"] = item['images'][2]['url']
            query["album_cover_small"] = item['images'][1]['url']
            query["album_cover_large"] = item['images'][0]['url']
            query["album_id"] = item['id']

            # use large image and resize
            img_url = item['images'][0]['url']

            with Image.open(session.get(img_url, stream = True).raw) as img:
                img.filename = img_url.rsplit('/', 1)[-1] + '.jpg'
                # This path needs to have write permissions for the executing user. 
                # typically 0775 for openhab:openhab 
                local_path = '/etc/openhab/html/spotify_api/images'

                if not os.path.exists(local_path):
                    os.mkdirs(local_path)
                
                img.resize((200,200),Image.ANTIALIAS).save(os.path.join(local_path, img.filename))
                query["album_cover_local"] = f'http://openhabian.home.wlan:8080/static/spotify_api/images/{img.filename}'

            _playlist.append(query)
        except (AttributeError, TypeError):
            continue
    return _playlist

def create_widget_file(content:str, playlist_name:str, destination:str = '.') -> None:
    """ create appropriate widget file from given data to import in openhab
    """
    if not os.path.exists(destination):
        os.mkdir(os.path.join(os.path.curdir,destination))

    openhab_widget = {}
    openhab_widget['template'] = content
    openhab_widget['id'] = playlist_name
    openhab_widget['settings'] = ''
    openhab_widget['name'] = f'Spotify Playlist - {playlist_name}'
    openhab_widget['author'] = u'Steffen Frömer'

    target_filename = playlist_name.replace(" ", "_").lower()
    target = os.path.join(destination, target_filename)

    with open(f'{target}.widget.json', 'w') as widget:
        widget.write(json.dumps(openhab_widget))


def get_playlist_from_spotify_playlist_url(spotify_client, playlist_url) -> list:
    """ """
    _playlist = []
    _content = query_spotify_api(spotify_client, playlist_url)
    album_ids = list(_content.keys())

    for album_id in album_ids:
        _playlist.extend(get_openhab_relevant_data_from_album(spotify_client, album_id))

    return _playlist
