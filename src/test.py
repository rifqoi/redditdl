import re
import os
import requests
from urllib import request
from urllib.request import urlopen, urlretrieve
import json
import sys

# Chech if the there is an argument or not
if len(sys.argv) >= 2:
    arg = sys.argv[1]
    # Check is the expected URL from reddit or not
    check_reddit = arg.startswith(('reddit.com/',
                                    'www.reddit.com/',
                                    'https://reddit.com/',
                                    'http://reddit.com/',
                                    'https://www.reddit.com/',
                                    'http://www.reddit.com/'
                                 ))
    
    if check_reddit:
        url = arg + ".json"
    else:
        sys.exit(0)
else:
    sys.exit(0)

# Get JSON String from the URL
url = url if url.startswith('http') else ('http://'+url)
response = urlopen(url)
data = response.read()
json_str = json.loads(data)

universal_url = json_str[0]["data"]["children"][0]["data"]["url_overridden_by_dest"]  

def get_res():
    fallback_link = json_str[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["fallback_url"]
    res_str = re.search(".*DASH_(.*)\.mp4.*", fallback_link).group(1)
    res = int(res_str)
    return res

def list_res(res):
    resolutions = [1080, 720, 480, 360]
    for i in range(len(resolutions)):
        if resolutions[i] == res:
            del resolutions[:i]
                       
    return resolutions
    
def get_video(res=None):
    default_res = get_res()
    default_url = universal_url+ "/DASH_" + str(default_res) + ".mp4" 

    if res:
        default_url = universal_url + "/DASH_" + str(res) + ".mp4" 
    return default_url


def get_audio():
    default_url = universal_url + "/DASH_audio.mp4" 
    return default_url

def check_audio():
    link = sys.argv[1]
    r = requests.get(link)
    web_content = r.headers['content-type']
    if web_content != "video/mp4":
        return False
    return True 

def set_environment_variable(path):
    cwd = os.getcwd()
    os.environ["REDDITDL_PATH"] = cwd
            
    if path:
        if path.startswith("/"):
            os.environ['REDDITDL_PATH'] = path

        else:
            home_dir = os.getenv('HOME', '-1')
            os.environ["REDDITDL_PATH"] = home_dir + "/" + path

    shell = os.getenv('SHELL', '-1')
    if "zsh" in shell:
        with open(os.path.expanduser("~/.zshrc"), "a") as outfile:
            outfile.write("export REDDITDL_PATH=" + "'" + os.getenv('REDDITDL_PATH', '-1') + "'" )
    elif "bash" in shell:
        with open(os.path.expanduser("~/.bashrc"), "a") as outfile:
            outfile.write("export REDDITDL_PATH=" + os.getenv('REDDITDL_PATH', '-1'))
    elif "fish" in shell:
        with open(os.path.expanduser("~/.config/fish/config.fish"), "a") as outfile:
            outfile.write("export REDDITDL_PATH=" + os.getenv('REDDITDL_PATH', '-1'))
    else:
        print('ERROR: You can manually add default location in your SHELL configuration file (i.e. .zshrc, .bashrc, etc.) by adding "export REDDITDL_PATH=/path/to/store/video"')

def download_video(res = None, path = None):
    # Filepath
    env_path = os.environ.get("REDDITDL_PATH", "-1")
    # env_path = os.getcwd() +"/"
    # Resolutions
    default_res = get_res()
    #Filename
    video_filename = re.search(".*it\/(.*).*", universal_url).group(1) 
    audio_filename = "aud"
    download_path = env_path + video_filename + ".mp4"
    audio_download_path = env_path + audio_filename + ".mp4"
    video_url = get_video(default_res)
    audio_url = get_audio()
    
    if res:
        video_url = get_video(res)
        
    if path:
        if path.startswith("/"):
            custom_path = path
        else:
            current_dir = os.getcwd()
            home_dir = os.getenv('HOME', '-1')
            if current_dir == home_dir:
                custom_path = home_dir + "/" + path
            else:
                custom_path = current_dir + "/" + path
            
        download_path = custom_path + video_filename + ".mp4"
        audio_download_path = custom_path + audio_filename + ".mp4"

    urlretrieve(video_url, download_path) 
    if check_audio():
        urlretrieve(audio_url, audio_download_path) 




def main():
    set_environment_variable("media/")
    download_video(360, path = "a/")

main()
