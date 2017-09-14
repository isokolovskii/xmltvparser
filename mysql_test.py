from mysql.connector import errorcode
from mysql.connector import connect
from mysql.connector import Error

# TODO: Search for config options
# TODO: Put mysql connection into function
# TODO: Config loads from file
# TODO: Functions for db manipulations
config = {
    'user': 'xmltvparser',
    'password': 'Ndgfhcth2017',
    'host': 'localhost',
    'database': 'tvservice',
    'raise_on_warnings': True,
}

try:
    cnx = connect(**config)

except Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cnx.close()
