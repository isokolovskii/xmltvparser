from mysql.connector import errorcode, connect, Error
from logger import info, debug, critical, error


class Database:
    # database connection config
    __config = {
        'user': 'xmltvparser',
        'password': 'Ndgfhcth2017',
        'host': 'localhost',
        'database': 'tvservice',
        'raise_on_warnings': True,
        'charset': 'utf8',
        'get_warnings': True
    }

    # initial tables
    __tables = {
        'channels': (
            "CREATE TABLE `channels` ("
            "   `id` INT NOT NULL,"
            "   `title` VARCHAR(255) NOT NULL,"
            "   `lang` VARCHAR(10) NOT NULL,"
            "   `icon` VARCHAR(255) DEFAULT NULL,"
            "PRIMARY KEY (id),"
            "UNIQUE(id),"
            "INDEX (id)"
            ") ENGINE=InnoDb DEFAULT CHARSET utf8"
        ),
        'categories': (
            "CREATE TABLE `categories` ("
            "   `id` INT NOT NULL AUTO_INCREMENT,"
            "   `title` VARCHAR(255) NOT NULL,"
            "   `lang` VARCHAR(10) NOT NULL,"
            "PRIMARY KEY (id),"
            "UNIQUE(id),"
            "INDEX (id)"
            ") ENGINE=InnoDb DEFAULT CHARSET utf8"
        ),
        'programme': (
            "CREATE TABLE `programme` ("
            "   `id` INT NOT NULL AUTO_INCREMENT,"
            "   `title` VARCHAR(255) NOT NULL,"
            "   `title_lang` VARCHAR(10) NOT NULL,"
            "   `start` DATETIME NOT NULL,"
            "   `end` DATETIME NOT NULL,"
            "   `duration` TIME NOT NULL,"
            "   `description` TEXT,"
            "   `description_lang` VARCHAR(10),"
            "   `channel_id` INT NOT NULL,"
            "PRIMARY KEY (id),"
            "INDEX (id),"
            "UNIQUE (channel_id, start, end),"
            "FOREIGN KEY (channel_id)"
            "    REFERENCES channels(id)"
            "    ON DELETE CASCADE"
            ") ENGINE=InnoDb DEFAULT CHARSET utf8"
        ),
        'programme_category': (
            "CREATE TABLE `programme_category` ("
            "   `programme_id` INT NOT NULL,"
            "   `category_id` INT NOT NULL,"
            "UNIQUE(programme_id, category_id),"
            "FOREIGN KEY (programme_id)"
            "    REFERENCES programme(id)"
            "    ON DELETE CASCADE,"
            "FOREIGN KEY (category_id)"
            "    REFERENCES categories(id)"
            "    ON DELETE CASCADE"
            ") ENGINE=InnoDB DEFAULT CHARSET utf8"
        )
    }

    # creates required variables
    def __init__(self):
        self.__err = None
        self.__connection = None
        self.__cursor = None
        self.__query = None

    # establish database connection
    def connect(self):
        try:
            connection = connect(**self.__config)
            connection.cursor()
        except Error as err:
            self.__err = err
            self.__error()
        else:
            self.__tables = self.__tables
            self.__connection = connection
            self.__cursor = connection.cursor()
            self.__create_tables()

    # disconnects from database
    def disconnect(self):
        self.__cursor.close()
        self.__connection.close()

    # runs prepared query with data
    def exec(self, data=None):
        try:
            # if data is None:
            #     debug(self.__query)
            # else:
            #     debug(self.__query % data)
            self.__cursor.execute(self.__query, data)
        except Error as err:
            self.__err = err
            return False
        else:
            if self.__query.startswith('INSERT') or self.__query.startswith('UPDATE') or self.__query.startswith(
                    'DELETE'):
                self.__connection.commit()
                return True
            else:
                result = self.__cursor.fetchall()
                return True, result

    # prepares query
    def prepare(self, query):
        self.__query = query

    # run query
    def query(self, query):
        self.prepare(query)
        run = self.exec()
        return run

    # id of last inserted row
    def last_insert_id(self):
        return self.__cursor.lastrowid

    # querying error message
    def error(self):
        return self.__err

    # logs error
    def __error(self):
        if self.__err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            critical('Something is wrong with your user name or password')
            exit(1)
        elif self.__err.errno == errorcode.ER_BAD_DB_ERROR:
            critical('Database does not exist')
            exit(1)
        else:
            error(self.__err)

    # creates initial tables
    def __create_tables(self, tables=__tables):
        failed_tables = {}
        for name, ddl in tables.items():
            try:
                self.__cursor.execute(ddl)
            except Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    info("Creating table {}: table already exists".format(name))
                else:
                    self.__err = err
                    self.__error()
                    failed_tables[name] = ddl
            else:
                info("Creating table {}: OK".format(name))
        if failed_tables:
            self.__create_tables(failed_tables)


if __name__ == "__main__":
    d = Database()
    d.connect()
