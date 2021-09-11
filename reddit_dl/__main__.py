import re
import sys
import os
import requests
from urllib.request import urlopen, urlretrieve
import json
import ffmpeg
from .args import parse_args

def check_link(url):
    check_reddit = url.startswith(('reddit.com/',
                                    'www.reddit.com/',
                                    'https://reddit.com/',
                                    'http://reddit.com/',
                                    'https://www.reddit.com/',
                                    'http://www.reddit.com/'
                                 ))
    
    if check_reddit:
        url = url if url.startswith('http') else ('http://'+url)
        url = url + ".json"
    else:
        print("Not a reddit url. Please input reddit url.")
        sys.exit()
    return url

def get_json(url):
    response = urlopen(url)
    data = response.read()

    return json.loads(data)

def list_res(json):
    fallback_link = json[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["fallback_url"]
    res_str = re.search(".*DASH_(.*)\.mp4.*", fallback_link).group(1)
    res = int(res_str)
    resolutions = [1080, 720, 480, 360]
    
    for i in range(len(resolutions)):
        if resolutions[i] == res:
            del resolutions[:i]
            break 
    return resolutions

def check_audio(json):
    universal_url = json[0]["data"]["children"][0]["data"]["url_overridden_by_dest"]  
    url = universal_url + "/DASH_audio.mp4" 
    r = requests.get(url)
    web_content = r.headers['content-type']
    if web_content != "video/mp4":
        return False
    
    return True 

def set_environment_variable(path):
    cwd = os.getcwd()
    os.environ["REDDITDL_PATH"] = cwd
            
    if path:
        if path.startswith("~"):
            path = os.path.expanduser(path)
            path = path if path.endswith("/") else path + "/"
            os.environ['REDDITDL_PATH'] = path

        else:
            path = os.path.abspath(path)
            path = path if path.endswith("/") else path + "/"
            os.environ["REDDITDL_PATH"] = path

    shell = os.getenv('SHELL', '-1')
    if "zsh" in shell:
        with open(os.path.expanduser("~/.zshrc"), "a") as outfile:
            outfile.write("export REDDITDL_PATH=" + "'" + os.getenv('REDDITDL_PATH', '-1') + "'" )
    elif "bash" in shell:
        with open(os.path.expanduser("~/.bashrc"), "a") as outfile:
            outfile.write("export REDDITDL_PATH=" + os.getenv('REDDITDL_PATH', '-1') + "'")
    elif "fish" in shell:
        with open(os.path.expanduser("~/.config/fish/config.fish"), "a") as outfile:
            outfile.write("export REDDITDL_PATH=" + os.getenv('REDDITDL_PATH', '-1' + "'"))
    else:
        print('ERROR: You can manually add default location in your SHELL configuration file (i.e. .zshrc, .bashrc, etc.) by adding "export REDDITDL_PATH=/path/to/store/video"')

def video_link(json, res=None):
    fallback_link = json[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["fallback_url"]
    universal_url = json[0]["data"]["children"][0]["data"]["url_overridden_by_dest"]  
    default_res = re.search(".*DASH_(.*)\.mp4.*", fallback_link).group(1)
    
    download_url = universal_url+ "/DASH_" + default_res + ".mp4" 
    if res:
        download_url = universal_url + "/DASH_" + str(res) + ".mp4" 

    return download_url

def audio_link(json):
    universal_url = json[0]["data"]["children"][0]["data"]["url_overridden_by_dest"]  
    download_url = universal_url + "/DASH_audio.mp4"

    return download_url

def download_path(path, universal_url, filename=None):
    video_filename = re.search(".*it\/(.*).*", universal_url).group(1) + "vid" + ".mp4"
    audio_filename = re.search(".*it\/(.*).*", universal_url).group(1) + "aud" + '.mp4'
    final_video = re.search(".*it\/(.*).*", universal_url).group(1) + ".mp4"

    if filename:
        video_filename = filename + "vid" + ".mp4"
        audio_filename = filename +"aud" + ".mp4"
        final_video = filename + ".mp4"

    if path.startswith("~"):
        path = os.path.expanduser(path)

    else:
        path = os.path.abspath(path)
        
    video_download_path = os.path.join(path , video_filename)
    audio_download_path = os.path.join(path , audio_filename)
    final_video_path = os.path.join(path, final_video)

    return video_download_path, audio_download_path, final_video_path

def download_video(json, video, filename = None, path = None):
    # Filepath
    universal_url = json[0]["data"]["children"][0]["data"]["url_overridden_by_dest"]  
    cwd = os.getcwd()
    name = None
    video_url = video

    if filename:
        name = filename

    video_download_path = download_path(cwd, universal_url, name)[0]
    if "REDDITDL_PATH" in os.environ:
        env_path = os.environ.get("REDDITDL_PATH", os.getcwd())
        video_download_path = download_path(env_path, universal_url, name)[0]
        
    if path:
        video_download_path = download_path(path, universal_url, name)[0]

    urlretrieve(video_url, video_download_path) 

def download_audio(json, audio, filename = None, path = None):
    # Filepath
    universal_url = json[0]["data"]["children"][0]["data"]["url_overridden_by_dest"]  
    cwd = os.getcwd()
    name = None
    audio_url = audio
    
    if filename:
        name = filename
        
    audio_download_path = download_path(cwd, universal_url, filename = name)[1]
        
    if "REDDITDL_PATH" in os.environ:
        env_path = os.environ.get("REDDITDL_PATH", os.getcwd())
        audio_download_path = download_path(env_path, universal_url, filename = name)[1]
        
    if path:
        audio_download_path = download_path(path, universal_url, filename=name)[1]

    urlretrieve(audio_url, audio_download_path) 
    
def merge(json, filename = None, path = None):
    universal_url = json[0]["data"]["children"][0]["data"]["url_overridden_by_dest"]  
    cwd = os.getcwd()
    name = None

    if filename:
        name = filename
        
    video, audio, final_video = download_path(cwd, universal_url, filename=name)
        
    if "REDDITDL_PATH" in os.environ:
        env_path = os.environ.get("REDDITDL_PATH", "-1")
        video, audio, final_video = download_path(env_path, universal_url, filename=name)
    
    if path:
        video, audio, final_video = download_path(path, universal_url, filename=name)
        
    import_video = ffmpeg.input(video)
    import_audio = ffmpeg.input(audio)
    print("Merging audio and video....")
    ffmpeg.concat(import_video, import_audio, v=1, a=1).output(final_video).run(quiet= True, overwrite_output = True)

    #remove file
    print("Removing audio and video....")
    os.remove(video)
    os.remove(audio)

def main():
    # print(check_audio())
    args = parse_args()
    url = check_link(args.url)
    print("Checking url...")
    json = get_json(url)
    print('Get JSON from URL....')
    check = check_audio(json)
    
    video = video_link(json)
    audio = audio_link(json)
    filename = None
            
    if args.url and args.list_resolution:
        l = list_res(json)
        print(l)
        
    else:
        if args.resolution:
            video = video_link(json, args.resolution)

        if args.rename:
            filename = args.rename
        
        if args.input_path:
            path = args.input_path
            download_video(json, video, filename, path)
            print("Downloading video....")
            if check:
                download_audio(json, audio, filename, path)
                print("Downloading audio.....")
                merge(json, filename, path)
        else:
            download_video(json, video, filename)
            print("Downloading video....")
            if check:
                download_audio(json, audio, filename)
                print("Downloading audio.....")
                merge(json, filename)
                
if __name__ == "__main__":
    main()
