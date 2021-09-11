from setuptools import setup

setup(
    name= 'redditdl',
    packages= ['reddit_dl'],
    version= '0.1',
    license= 'MIT',
    author= 'Muhammad Rifqi Al Furqon',
    author_email= 'alfurqon.rifqi@gmail.com',
    description= 'Download reddit video through command line.',
    entry_points= {'console_scripts' : ['redditdl= reddit_dl.__main__:main']},
    install_requires=['ffmpeg-python', 'urllib3']
)
