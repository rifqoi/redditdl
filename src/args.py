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
            "-d",
            "--default-path",
            type = str,
            help="Specify default path of the downloaded video."
            )
    
    parser.add_argument(
            "-i",
            type= str,
            help="Specify the path of current downloaded video."
            )
    return parser.parse_args()
    
