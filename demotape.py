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
import ntpath
import yaml
from pathlib import Path

config_path = Path(__file__).parent / './config.yaml'
with config_path.open() as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

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


def timestamp():
    dateTimeObj = datetime.now()
    return '[ ' + dateTimeObj.strftime("%F %H:%M:%S.%f") + ' ]  '



def generate_channellist():
    channels = []
    districts = range(1, 23 + 1) # districts of vienna

    for district_num in districts:
        # district_str = str(district_num)
        district_str_lz = str(district_num).zfill(2) # leading zero
        channel = {
                'name': '1' + district_str_lz + '0',  # 1010 - 1230
                'url': 'https://stream.wien.gv.at/live/ngrp:bv' + district_str_lz + '.stream_all/playlist.m3u8'
            }
        channels.append(channel)
    print('channels:')
    for channel in channels:
        print(channel['name'] + ' ' + channel['url'])
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
        print(timestamp() + 'Done downloading!')
    else:
        print(timestamp() + 'sth went wrong' + d['status'])
    print(d)


def download_stream(channel, dest_path):
    print('download_stream')
    ytdl_opts = {
            'logger': MyLogger(),
            'outtmpl': dest_path,
            'format': 'bestaudio/best',
            # 'recodevideo': 'mp4',
            # 'postprocessors': [{
            #     'key': 'FFmpegVideoConvertor',
            #     'preferedformat': 'mp4',
            #     'preferredquality': '25',
            # }],
            # should just stop after a few retries and start again instead of hanging in the loop of trying to download
            'retries': 3, 
            'fragment-retries': 3,
            'progress_hooks': [my_ytdl_hook]
        }
    ytdl = youtube_dl.YoutubeDL(ytdl_opts)

    try:
        print(timestamp() + " Downloading: " + channel['url'])
        ytdl.download([channel['url']])
    except (youtube_dl.utils.DownloadError) as e:
        print(timestamp() + " Download error: " + str(e))
    except (youtube_dl.utils.SameFileError) as e:
        print("Download error: " + str(e))
    except (UnicodeDecodeError) as e:
        print("UnicodeDecodeError: " + str(e))


def process_channel(channel):
    #print('entered function process_channel with ' + channel['name'])
    while True:

        print(timestamp() + ' checking ' + channel['name'])
        if check_stream(channel['url']):
            print(channel['name'] + ': stream online! Downloading ...')
            dest_dir = ROOT_PATH + '/' + channel['name'] +'/'
            # create directory if it doesn't exist
            if not os.path.exists(dest_dir):
                print('creating directory ' + dest_dir)
                os.makedirs(dest_dir)
            dest_path = get_destpath(channel) # dirctory + filename
            download_stream(channel, dest_path) # also converts video
            print(timestamp() + " Uploading video " + dest_path)
            upload_video(dest_path)
        else:
            waitingtime = random.randint(50,60)
            time.sleep(waitingtime)


    print('end processing ' + channel['name'] + ' ... (shouldn\'t happen!)')


def upload_video(videofile_path):
    print('uploading %s' % (videofile_path))
    credentials = config['webdav']['username'] + ':' + config['webdav']['password']
    webdav_baseurl = config['webdav']['base_url']
    filename = ntpath.basename(videofile_path)
    webdav_url = webdav_baseurl + filename
    try:
        # Upload to cloud using webdav
        result = os.system('curl -L -u %s -T "%s" "%s"' % (credentials, videofile_path, webdav_url))
        if result == 0: # exit code
            delete_video(videofile_path)
            return true
    except:
        print('Error while uploading %s to %s' % (file, webdav_url))
 

def delete_video(file):
    try:
        os.system('rm -rf "%s"' % (file))
        return true
    except:
        print('Error while deleting %s' % (file))


def get_destpath(channel):
    now = datetime.now() # current date and time
    dest_dir = ROOT_PATH + '/' + channel['name'] +'/'
    dest_filename = channel['name'] + "_" + now.strftime("%Y-%m-%d--%H.%M.%S") + '.mp4'
    return dest_dir + dest_filename


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
