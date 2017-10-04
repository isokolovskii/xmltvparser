import gzip
import os
import shutil
from xml.etree.ElementTree import parse

import requests
from dateutil import parser

from database import Database
from logger import info, error, critical


class XmlParser:
    # source xml file
    __file = '/tmp/xmltv.xml'
    __gz_file = '/tmp/xmltv.xml.gz'
    __url = 'http://www.teleguide.info/download/new3/xmltv.xml.gz'

    def __init__(self):
        # load xml file from remote hostNone
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
        self.__generator_name = self.__root.get("generator-info-name")
        self.__generator_url = self.__root.get("generator-info-url")
        info('Generator: {}, url: {}'.format(self.__generator_name, self.__generator_url))
        # database connection
        self.__database = Database()
        self.__database.connect()
        self.__db_channels = {}
        self.__load_db_channels()
        self.__db_categories = {}
        self.__load_db_categories()

    # starts parsing
    def parse(self):
        self.__parse_channels()
        self.__parse_programme()
        self.__clean_up()
        os.remove(self.__file)
        info('Parsing complete')

    # parse channel list
    def __parse_channels(self):
        info("Start channel parsing...")
        for channel in self.__root.findall('channel'):
            # channel data
            channel_id = int(channel.get('id'))
            title = channel.find('display-name').text
            lang = channel.find('display-name').get('lang')
            icon = ''
            if channel.find('icon') is not None:
                icon = channel.find('icon').get('src')
            # check if id already exists
            if channel_id in self.__db_channels.keys():
                self.__db_channels[channel_id]['delete'] = False
                # check if data changed and update it
                if icon != self.__db_channels[channel_id]['icon'] or title != self.__db_channels[channel_id]['title'] \
                        or lang != self.__db_channels[channel_id]['lang']:
                    result = self.__database.query("UPDATE channels SET title=\'" + title + "\', lang=\'" + lang +
                                                   "\', icon=\'" + icon + "\' WHERE id=" + str(channel_id))
                    if result:
                        info("Channel updated: " + str(channel_id))
                    else:
                        error(self.__database.error())
                continue

            # insert data into database
            self.__database.prepare("INSERT INTO channels (id, title, lang, icon) VALUES (%s, %s, %s, %s)")
            result = self.__database.exec((channel_id, title, lang, icon))
            if not result:
                error(self.__database.error())
            info("Channel {} {} added.".format(channel_id, title))
            self.__db_channels[channel_id] = {
                'title': title,
                'lang': lang,
                'icon': icon,
                'delete': False
            }
        info("Channel parsing completed")

    # parse programme
    def __parse_programme(self):
        info("Start programme parsing...")
        for programme in self.__root.findall('programme'):
            # programme main data
            begin = programme.get('start')
            begin = parser.parse(begin)
            end = programme.get('stop')
            end = parser.parse(end)
            duration = end - begin
            channel_id = int(programme.get('channel'))
            title = programme.find('title').text
            title_lang = programme.find('title').get('lang')

            # programme categories
            categories = self.__parse_categories(programme.findall('category'))

            # programme descriptions
            description = ''
            description_lang = ''
            if programme.find('desc') is not None:
                description = programme.find('desc').text
                description_lang = programme.find('desc').get('lang')

            # add programme or update if it exists
            result = self.__database.query("SELECT id, title, title_lang, end, duration, description "
                                           ", description FROM programme WHERE channel_id=" +
                                           str(channel_id) + " AND begin=\'" + begin.strftime('%Y-%m-%d %H:%M:%S') +
                                           "\'")
            pid = -1
            if not result:
                error(self.__database.error())
            if result[1]:
                for programme_id, t, tl, e, d, desc, descl in result[1]:
                    pid = programme_id
                    if t != title or tl != title_lang or end.strftime('%Y-%m-%d %H:%M:%S') != \
                            e.strftime('%Y-%m-%d %H:%M:%S') or d != duration or desc != description or descl != \
                            description_lang:
                        result = self.__database.query("UPDATE programme SET title=\'" + title + "\', title_lang=\'" +
                                                       title_lang + "\', end=\'" +
                                                       end.strftime('%Y-%m-%d %H:%M:%S') + "\', duration=\'" +
                                                       str(duration) + "\', description=\'" + description +
                                                       "\', description_lang=\'" + description_lang +
                                                       "\' WHERE id=" + str(pid))
                        if result:
                            info("Programme updated: " + str(pid))
                        else:
                            error(self.__database.error())
            else:
                self.__database.prepare("INSERT INTO programme (title, title_lang, begin, end, duration, description, "
                                        "description_lang, channel_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
                result = self.__database.exec((title, title_lang, begin, end, duration, description, description_lang,
                                               channel_id))
                if not result:
                    error(self.__database.error())
                    continue
                pid = self.__database.last_insert_id()

            # clear all categories for pid if exists and add anew
            result = self.__database.query("DELETE FROM programme_category WHERE programme_id=%s" % pid)
            if not result:
                error(self.__database.error())
            self.__database.prepare("INSERT INTO programme_category (programme_id, category_id) VALUES (%s, %s)")
            for category_id in categories:
                result = self.__database.exec((pid, category_id))
                if not result:
                    error(self.__database.error())
                    continue
        info("Programme parsing completed")

    # parse programme categories
    def __parse_categories(self, categories):
        c = []
        for category in categories:
            if category.text not in self.__db_categories.values():
                result = self.__database.query("INSERT INTO categories (title, lang) VALUES (\'%s\', \'%s\')" %
                                               (category.text, category.get('lang')))
                if not result:
                    error(self.__database.error())
                info('Add category {} to database, id {}'.format(category.text, self.__database.last_insert_id()))
                c.append(self.__database.last_insert_id())
                self.__db_categories[self.__database.last_insert_id()] = category.text
            else:
                result = self.__database.query("SELECT id FROM categories WHERE title=\'%s\' LIMIT 1" %
                                               category.text)
                if not result[0]:
                    critical(self.__database.error())
                    exit(1)
                for i in result[1]:
                    c.append(i[0])
        return c

    # load existing channels from database
    def __load_db_channels(self):
        result = self.__database.query("SELECT * FROM channels")
        if not result[0]:
            critical(self.__database.error())
            exit(1)
        for channel_id, title, lang, icon in result[1]:
            self.__db_channels[channel_id] = {
                'title': title,
                'lang': lang,
                'icon': icon,
                'delete': True
            }

    # load existing categories from database
    def __load_db_categories(self):
        result = self.__database.query("SELECT id, title FROM categories")
        if not result[0]:
            critical(self.__database.error())
            exit(1)
        for cat_id, title in result[1]:
            self.__db_categories[cat_id] = title

    # clear old data
    def __clean_up(self):
        # remove old programme
        result = self.__database.query("DELETE FROM programme WHERE end < DATE_SUB(NOW(), INTERVAL 7 DAY)")
        if result:
            info("Old programme removed")
        else:
            error(self.__database.error())

        # remove unknown channels
        self.__database.prepare("DELETE FROM channels WHERE id=%s")
        for channel_id in self.__db_channels.keys():
            if self.__db_channels[channel_id]['delete']:
                result = self.__database.prepare("DELETE FROM channels WHERE id=" + str(channel_id))
                if not result:
                    error(self.__database.error())
                else:
                    info("Unknown channel removed " + str(channel_id))
