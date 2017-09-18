import gzip
import os
import shutil
from xml.etree.ElementTree import parse
import requests
from dateutil import parser
from database import Database
from logger import info


# TODO: May be more than one category
# TODO: May be titles in different languages
# TODO: Add credits
class XmlParser:
    # source xml file
    __file = '/tmp/xmltv.xml'
    __gz_file = '/tmp/xmltv.xml.gz'
    __url = 'http://www.teleguide.info/download/new3/xmltv.xml.gz'

    def __init__(self):
        # load xml file from remote host
        info('Loading xml file...')
        r = requests.get(self.__url)
        with open(self.__gz_file, 'wb') as output:
            output.write(r.content)
        with gzip.open(self.__gz_file, 'rb') as f_in, open(self.__file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(self.__gz_file)
        info('Xml file loaded')
        # parse xml tv file into object and get root object
        self.__tree = parse(self.__file)
        self.__root = self.__tree.getroot()
        # generator info
        # self.__generator_name = self.__root.find("tv").get("generator-info-name")
        # self.__generator_url = self.__root.find("tv").get("generator-info-url")
        # database connection
        self.__database = Database()
        self.__database.connect()
        self.__db_channels = {}
        self.__load_db_channels()

    # starts parsing
    def parse(self):
        self.__parse_channels()
        # self.__parse_programme()
        os.remove(self.__file)
        info('Parsing complete')

    # parse channel list
    def __parse_channels(self):
        info("Start channel parsing...")
        self.__database.prepare("INSERT INTO channels (id, title, lang, icon) VALUES (%s, %s, %s, %s)")
        for channel in self.__root.findall('channel'):
            channel_id = int(channel.get('id'))
            title = channel.find('display-name').text
            if channel_id in self.__db_channels.keys():
                info("Channel {} {} is already in table".format(channel_id, title))
                continue
            lang = channel.find('display-name').get('lang')
            icon = ''
            if channel.find('icon') is not None:
                icon = channel.find('icon').get('src')
            self.__database.run((channel_id, title, lang, icon))
            self.__db_channels[channel_id] = {
                'title': title,
                'lang': lang,
                'icon': icon
            }
        info("Channel parsing completed")

    # parse programme
    def __parse_programme(self):
        info("Start programme parsing...")
        for programme in self.__root.findall('programme'):
            start = programme.get('start')
            start = parser.parse(start)
            stop = programme.get('stop')
            stop = parser.parse(stop)
            duration = stop - start
            channel_id = int(programme.get('channel'))
            title = programme.find('title').text
            title_lang = programme.find('title').get('lang')
            category = ''
            category_lang = ''
            if programme.find('category') is not None:
                category = programme.find('category').text
                category_lang = programme.find('category').get('lang')
            desc = ''
            desc_lang = ''
            if programme.find('desc') is not None:
                desc = programme.find('desc').text
                desc_lang = programme.find('desc').get('lang')
            print(start.isoformat(), stop.isoformat(), duration, channel_id, title, title_lang, category, category_lang,
                  desc, desc_lang, sep=' ')
        info("Programme parsing completed")

    def __load_db_channels(self):
        db_channels = self.__database.query("SELECT * FROM channels")
        for channel_id, title, lang, icon in db_channels:
            self.__db_channels[channel_id] = {
                'title': title,
                'lang': lang,
                'icon': icon
            }
