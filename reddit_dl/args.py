import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Reddit Video Downloader using Python")

    parser.add_argument(
            "--list-resolution",
            "-l",
            action="store_true",
            help="List all available resolutions"
            )

    parser.add_argument(
            "--input-path",
            "-i",
            type= str,
            help="Specify the path of current downloaded video."
            )
    parser.add_argument(
            "--rename",
            "-rn",
            type= str,
            help="Rename the video."
            )
    parser.add_argument(
            "--resolution",
            "-r",
            type= str,
            help="Specify video resolution you want to download."
            )
    parser.add_argument(
            "url",
            help = "Input reddit vide url you want to download.",
            type=str
            )
    return parser.parse_args()
    
