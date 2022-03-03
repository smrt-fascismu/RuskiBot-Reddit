from contextlib import contextmanager
from os import getenv

from pymysql import connect


class Connector:
    @contextmanager
    def get_conn(self):
        with connect(user=getenv('db_user'), host=getenv('db_host'), port=int(getenv('db_port')),
                     password=getenv('db_password'), database=getenv('db'), autocommit=True) as connection:
            cursor = connection.cursor()
            yield cursor
