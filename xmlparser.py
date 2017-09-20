import gzip
import os
import requests
import shutil
from xml.etree.ElementTree import parse
from dateutil import parser
from database import Database
from logger import info


# TODO: May be titles in different languages
# TODO: Duration may be longer than 24hrs
# TODO: Add other attributes of programme
# TODO: Check if programme already exists
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
                continue
            lang = channel.find('display-name').get('lang')
            icon = ''
            if channel.find('icon') is not None:
                icon = channel.find('icon').get('src')
            self.__database.run((channel_id, title, lang, icon))
            info("Channel {} {} added.".format(channel_id, title))
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
            # programme main data
            start = programme.get('start')
            start = parser.parse(start)
            end = programme.get('stop')
            end = parser.parse(end)
            duration = end - start
            channel_id = int(programme.get('channel'))
            title = programme.find('title').text
            title_lang = programme.find('title').get('lang')
            # programme categories
            categories = self.__parse_categories(programme.findall('category'))
            # # programme descriptions
            # description = []
            # for desc in programme.findall('desc'):
            #     description.append({
            #         'desc': desc.text,
            #         'desc_lang': desc.get('lang')
            #     })
            # # programme sub-titles
            # sub_titles = []
            # for sub_title in programme.findall('sub-title'):
            #     sub_titles.append({
            #         'subtitle': sub_title.text,
            #         'subtitle_lang': sub_title.get('lang')
            #     })
            # # credits of programme
            # programme_credits = {}
            # if programme.find('credits') is not None:
            #     credit = programme.find('credits')
            #     actors = []
            #     directors = []
            #     writers = []
            #     adapters = []
            #     producers = []
            #     composers = []
            #     editors = []
            #     presenters = []
            #     commentators = []
            #     guests = []
            #     for actor in credit.findall('actors'):
            #         actors.append(actor.text)
            #     for writer in credit.findall('writers'):
            #         writers.append(writer.text)
            #     for director in credit.findall('directors'):
            #         directors.append(director.text)
            #     for adapter in credit.findall('adapters'):
            #         adapters.append(adapter.text)
            #     for producer in credit.findall('producers'):
            #         producers.append(producer.text)
            #     for composer in credit.findall('composers'):
            #         composers.append(composer.text)
            #     for editor in credit.findall('editors'):
            #         editors.append(editor.text)
            #     for presenter in credit.findall('presenters'):
            #         presenters.append(presenter.text)
            #     for commentator in credit.findall('commentators'):
            #         commentators.append(commentator.text)
            #     for guest in credit.findall('guests'):
            #         guests.append(guest.text)
            #     programme_credits['actors'] = actors
            #     programme_credits['writers'] = writers
            #     programme_credits['directors'] = directors
            #     programme_credits['adapters'] = adapters
            #     programme_credits['producers'] = producers
            #     programme_credits['composers'] = composers
            #     programme_credits['editors'] = editors
            #     programme_credits['presenters'] = presenters
            #     programme_credits['commentators'] = commentators
            #     programme_credits['guests'] = guests
            # # programme keywords
            # keywords = []
            # for keyword in programme.findall('keyword'):
            #     keywords.append({
            #         'keyword': keyword.text,
            #         'keyword_lang': keyword.get('lang')
            #     })
            # # programme icon
            # icons = []
            # for icon in programme.findall('icon'):
            #     icons.append({
            #         'src': icon.get('src'),
            #         'width': icon.get('width'),
            #         'height': icon.get('height')
            #     })
            # countries = []
            # # programme country(production and assoc)
            # for country in programme.findall('country'):
            #     lang = ''
            #     if country.get('lang') is not None:
            #         lang = country.get('lang')
            #     countries.append({
            #         'country': country.text,
            #         'lang': lang
            #     })
            # # programme ratings
            # ratings = []
            # for rating in programme.findall('rating'):
            #     icon = ''
            #     if rating.find('icon') is not None:
            #         icon = rating.find('icon').get('src')
            #     system = ''
            #     if rating.get('system') is not None:
            #         system = rating.get('system')
            #     ratings.append({
            #         'value': rating.find('value').text,
            #         'icon': icon,
            #         'system': system
            #     })
            # # programme stars
            # star_ratings = []
            # for star_rating in programme.findall('star_rating'):
            #     icon = ''
            #     if star_rating.find('icon') is not None:
            #         icon = rating.find('icon').get('src')
            #     system = ''
            #     if star_rating.get('system') is not None:
            #         system = star_rating.get('system')
            #     star_ratings.append({
            #         'value': rating.find('value').text,
            #         'icon': icon,
            #         'system': system
            #     })
            self.__database.prepare("INSERT INTO programme (title, title_lang, start, end, duration, channel_id)"
                                    "VALUES (%s, %s, %s, %s, %s, %s)")
            self.__database.run((title, title_lang, start, end, duration, channel_id))
            programme_id = self.__database.last_insert_id()
            self.__database.prepare("INSERT INTO programme_category (programme_id, category_id) VALUES (%s, %s)")
            for category_id in categories:
                self.__database.run((programme_id, category_id))
        info("Programme parsing completed")

    # parse programme categories
    def __parse_categories(self, categories):
        c = []
        for category in categories:
            if category.text not in self.__db_categories.values():
                self.__database.query("INSERT INTO categories (title, lang) VALUES (\'%s\', \'%s\')" %
                                      (category.text, category.get('lang')))
                info('Add category {} to database, id {}'.format(category.text, self.__database.last_insert_id()))
                c.append(self.__database.last_insert_id())
                self.__db_categories[self.__database.last_insert_id()] = category.text
            else:
                category_id = self.__database.query("SELECT id FROM categories WHERE title=\'%s\' LIMIT 1" %
                                                    category.text)
                for i in category_id:
                    c.append(i[0])
        return c

    # load existing channels from database
    def __load_db_channels(self):
        db_channels = self.__database.query("SELECT * FROM channels")
        for channel_id, title, lang, icon in db_channels:
            self.__db_channels[channel_id] = {
                'title': title,
                'lang': lang,
                'icon': icon
            }

    # load existinng categorues from database
    def __load_db_categories(self):
        db_categories = self.__database.query("SELECT id, title FROM categories")
        for cat_id, title in db_categories:
            self.__db_categories[cat_id] = title
