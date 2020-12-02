# demotape.py checks regulary the webstreams of all district parlaments 
# in Vienna. If a webstream is online, it gets recorded into seperate 
# directories per district.

import os
import sys
import time
from datetime import datetime
import random
import m3u8
import youtube_dl
import asyncio
import concurrent.futures



try:
    if sys.argv[1] and os.path.exists(sys.argv[1]):
        ROOT_PATH = sys.argv[1]
        print('Root path for downloaded streams: ' + ROOT_PATH)
    else:
        print('destination path does not exist')
        sys.exit()
except IndexError:
    print('Script needs a valid destination path for recorded videos as argument')
    print('For example: \ndemotape.py /path/to/videos')
    sys.exit()






def generate_channellist():
    channels = []
    districts = range(1, 23 + 1) # districts of vienna

    for district_num in districts:
        district_str = str(district_num)
        district_str_lz = str(district_num).zfill(2) # leading zero
        channel = {
                'name': district_str+'. Bezirk',
                'url': 'https://stream.wien.gv.at/live/ngrp:bv' + district_str_lz + '.stream_all/playlist.m3u8'
            }
        channels.append(channel)
    return channels


def check_stream(url):
    playlist = m3u8.load(url)
    try: 
        if playlist.data['playlists']:
            # has active live stream
            return True
        else:
            # no livestream
            return False
    except (ValueError, KeyError):
        print('some connection error or so')



class MyLogger(object):
    def debug(self, msg):
        #pass
        print(msg)

    def warning(self, msg):
        #pass
        print(msg)

    def error(self, msg):
        print(msg)


def my_ytdl_hook(d):
    if d['status'] == 'finished':
        print('Done downloading!')
        print(d)


def download_stream(channel):
    now = datetime.now() # current date and time

    dest_dir = ROOT_PATH + '/' + channel['name'] +'/'
    dest_filename = now.strftime("%Y-%m-%d--%H.%M.%S") + '.mp4'

    # create directory if it doesn't exist
    if not os.path.exists(dest_dir):
        print('creating directory ' + dest_dir)
        os.makedirs(dest_dir)
    
    dest = dest_dir + dest_filename

    ytdl_opts = {
            'logger': MyLogger(),
            'outtmpl': dest,
            'format': 'bestaudio/best',
            'recodevideo': 'mp4',
            'progress_hooks': [my_ytdl_hook],
        }

    ytdl = youtube_dl.YoutubeDL(ytdl_opts)

    try:
        ytdl.download([channel['url']])
    except (youtube_dl.utils.DownloadError) as e:
        print("Download error: " + str(e))
    except (youtube_dl.utils.SameFileError) as e:
        print("Download error: " + str(e))
    except (UnicodeDecodeError) as e:
        print("UnicodeDecodeError: " + str(e))



def process_channel(channel):
    #print('entered function process_channel with ' + channel['name'])
    while True:
        #print('checking ' + channel['name'])
        if check_stream(channel['url']):
            print(channel['name'] + ': stream online! Downloading ...')
            download_stream(channel)
        else:
            # print(channel['name'] + ': stream offline')
            # wait between checks
            waitingtime = random.randint(20,30)
            time.sleep(waitingtime)

    print('end processing ' + channel['name'] + ' ... (shouldn\'t happen!)')




def main():
    channels = generate_channellist()

    with concurrent.futures.ThreadPoolExecutor(max_workers=23) as executor:
        future_to_channel = {executor.submit(process_channel, channel): channel for channel in channels}

    for future in concurrent.futures.as_completed(future_to_channel):
        channel = future_to_channel[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (channel, exc))
        else:
            print('%r page is %d bytes' % (channel, len(data)))


    print('end main (this shouldn\'t happen!)')


main()






#test_channel = {
#           'name': 'Test Channel', 
#           'url': 'https://1000338copo-app2749759488.r53.cdn.tv1.eu/1000518lf/1000338copo/live/app2749759488/w2928771075/live247.smil/playlist.m3u8'
#       }
#download_stream(test_channel)
