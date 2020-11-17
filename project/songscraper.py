# Make HTTP requests
import requests
# Scrape data from an HTML document
from bs4 import BeautifulSoup
# I/O
import os
# Search and manipulate strings
import re
import sys
import time

GENIUS_API_TOKEN='ELm-2kfPQk1HpTbiPswUiuhegHiNc1OTTx-sUXUpOpf23FWwSmunES4nsQ4gLhnK'

# Get artist object from Genius API
def request_artist_info(artist_name, page):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + GENIUS_API_TOKEN}
    search_url = base_url + '/search?per_page=10&page=' + str(page)
    data = {'q': artist_name}
    response = requests.get(search_url, data=data, headers=headers)
    # print("found information for", artist_name)
    return response

# Get Genius.com song url's from artist object
def request_song_url(artist_name, song_cap):
    # print("requesting song url")
    page = 1
    songs = []
    last_found_time = time.time()
    while time.time() - last_found_time <= 10 and len(songs) < song_cap:
        # print("inside while loop")
        response = request_artist_info(artist_name, page)
        json = response.json()
        # Collect up to song_cap song objects from artist
        song_info = []
        for hit in json['response']['hits']:
            # print("inside hit")
            if artist_name.lower() == hit['result']['primary_artist']['name'].lower():
                song_info.append(hit)
                last_found_time = time.time()
    
        # Collect song URL's from song objects
        for song in song_info:
            if (len(songs) < song_cap):
                url = song['result']['url']
                songs.append(url)
            
        # if (len(songs) == song_cap):
        #     break
        # else:
        page += 1
        
    print('Found {} songs by {}'.format(len(songs), artist_name))
    return songs

def get_lyrics(url, triesLeft):
    if triesLeft <= 0:
        return ""
    # print("url", url)
    page = requests.get(url)
    # print("page", page)
    html = BeautifulSoup(page.text, 'html.parser')
    # print("html", html)
    lyricsmaybe = html.find('div', class_='lyrics')
    if lyricsmaybe != None:
        return lyricsmaybe.get_text()
    if lyricsmaybe == None:
        return get_lyrics(url, triesLeft-1)

# Scrape lyrics from a Genius.com song URL
def scrape_song_lyrics(url):
    lyrics = get_lyrics(url, 10)
    #remove identifiers like chorus, verse, etc
    lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
    #remove empty lines
    lyrics = os.linesep.join([s for s in lyrics.splitlines() if s])         
    return lyrics

def write_lyrics_to_file(artist_name, song_count):
    f = open('lyrics/' + artist_name.lower() + '.txt', 'wb')
    urls = request_song_url(artist_name, song_count)
    for url in urls:
        lyrics = scrape_song_lyrics(url)
        if lyrics != "":
            f.write(lyrics.encode("utf8"))
            f.write("\n\n----------\n\n".encode("utf8"))
    f.close()
    num_lines = sum(1 for line in open('lyrics/' + artist_name.lower() + '.txt', 'rb'))
    print('Wrote {} lines to file from {} songs'.format(num_lines, song_count))
  
# DEMO
artist = sys.argv[1]
song_count = 180
if len(sys.argv) > 2:
    song_count = int(sys.argv[2])
write_lyrics_to_file(artist, song_count)

# # DEMO
# print(scrape_song_lyrics('https://genius.com/Lana-del-rey-young-and-beautiful-lyrics'))
    
# # DEMO
# request_song_url('Lana Del Rey', 2)