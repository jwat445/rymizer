"""
This is a script that retrieves the genres
and descriptors of all albums in the given
folder from rateyourmusic.com and edits the 
.mp3 files to have those genres and descriptors

Usage: python rymizer.py 'YOUR MUSIC DIRECTORY'
EX: python rymizer.py /Users/Joshua/Downloads
Your music directory must be organized by
artist and each artist directory should
be organized by album

Written by: Joshua Watson using the following libraries:
https://pypi.python.org/pypi/beautifulsoup4
https://github.com/pgaref/HTTP_Request_Randomizer
https://mutagen.readthedocs.io/en/latest/user/id3.html
"""

import sys
import os
import time
import requests
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
import re
from bs4 import BeautifulSoup
from mutagen.easyid3 import EasyID3

# Gets info of the album from rateyourmusic.com
def getInfo(artist, album, dir):
    artist = artist.replace(' ', '-').lower()
    album = album.replace(' ', '-').lower()

    # Get the album page
    url = "https://rateyourmusic.com/release/album/" + artist +  "/" + album + "/"
    print "\nGETTING: ", url + '\n'
    req_proxy = RequestProxy()
    page = req_proxy.generate_proxied_request(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get genres from page
    genre_text = str(soup.findAll("span", {"class": "release_pri_genres"}))
    # Get secondary genres from page
    sec_genre_text = str(soup.findAll("span", {"class": "release_sec_genres"}))
    # Clean up and compile all genres
    unclean_genres = re.findall(r']">.*?</a>', genre_text)
    unclean_sec_genres = re.findall(r']">.*?</a>', sec_genre_text)
    genres = []
    for genre in unclean_genres:
        genre = genre[3:-4]
        genres.append(genre)
    for genre in unclean_sec_genres:
        genre = genre[3:-4]
        genres.append(genre)

    # Get descriptors from page
    descriptor_text = str(soup.findAll("span", {"class": "release_pri_descriptors"}))
    descriptor_text = descriptor_text[37:-7]
    # Clean up and organize each descriptor
    unclean_descriptors = re.findall(r'.*?,', descriptor_text)
    descriptors = []
    for descriptor in unclean_descriptors:
        descriptor = descriptor[2:-1]
        descriptors.append(descriptor)

    # Print genres
    genres = ';'.join(genre for genre in genres)
    print (artist + '->' + album + ' genres:'),
    print genres

    # Print descriptors
    descriptors = 'blerp' #WE ARENT GETTING DESCRIPTORS???? AR ETHEY BEING OVERRIDDEN SOMEHOW???
    descriptors = ';'.join(descriptor for descriptor in descriptors)
    print (artist + '->' + album + ' descriptors:'),
    print descriptors

    #Put the genres in the files
    files = os.listdir(dir)
    for file in files:
        if str(file).endswith('.mp3'):
            print file
            audio = EasyID3(dir + '/' + file)
            audio["genre"] = genres
            EasyID3.RegisterTextKey('comment', 'COMM')
            audio['comment'] = descriptors
            audio["mood"] = descriptors
            audio.save(v2_version=3)
            print('Genres updated: ' + str(audio["genre"]))
            print('Descriptors (mood) updated: ' + str(audio["mood"]))

# Main function, goes through the given directory and finds albums to getInfo()
if __name__ == "__main__":
    music_dir = sys.argv[1]
    artists = next(os.walk(music_dir))[1]
    for artist in artists:
        artist_dir = os.path.join(music_dir, artist)
        albums = next(os.walk(artist_dir))[1]
        for album in albums:
            album_dir = os.path.join(artist_dir, album)
            getInfo(artist, album, album_dir)
            time.sleep(1)
    print "DONE!"
