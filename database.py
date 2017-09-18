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
    __tables = {'channels': (
        "CREATE TABLE `channels` ("
        "   `id` INT NOT NULL,"
        "   `title` VARCHAR(255) NOT NULL,"
        "   `lang` VARCHAR(10) NOT NULL,"
        "   `icon` VARCHAR(255) DEFAULT NULL,"
        "PRIMARY KEY (id),"
        "UNIQUE(id)"
        ") ENGINE=InnoDb DEFAULT CHARSET utf8"
    )}

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
            self.__log_error()
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
    def run(self, data=None):
        try:
            if data is None:
                debug(self.__query)
            else:
                debug(self.__query % data)
            self.__cursor.execute(self.__query, data)
        except Error as err:
            self.__err = err
            self.__log_error()
        else:
            if self.__query.startswith('INSERT') or self.__query.startswith('UPDATE'):
                self.__connection.commit()
            else:
                result = self.__cursor.fetchall()
                return result

    # prepares query
    def prepare(self, query):
        self.__query = query

    # run query
    def query(self, query):
        self.prepare(query)
        run = self.run()
        if run is not None:
            return run

    # logs error
    def __log_error(self):
        if self.__err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            critical('Something is wrong with your user name or password')
            exit(1)
        elif self.__err.errno == errorcode.ER_BAD_DB_ERROR:
            critical('Database does not exist')
            exit(1)
        else:
            error(self.__err)

    # creates initial tables
    def __create_tables(self):
        for name, ddl in self.__tables.items():
            try:
                self.__cursor.execute(ddl)
            except Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    info("Creating table {}: table already exists".format(name))
                else:
                    self.__err = err
                    self.__log_error()
            else:
                info("Creating table {}: OK".format(name))
