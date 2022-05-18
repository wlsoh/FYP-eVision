# Developer Name: Soh Wee Liam
# Intake: UC3F2111CS(IS)
# Program Name: DB Connection
# Date Created: 05/05/2022
import configparser
import pymysql
from pymysql.constants import CLIENT

# Connector class
class MySqlConnector(object):
    def __init__(self, env=None):
        cf = configparser.ConfigParser()
        cf.read('mysql_db/mysql_config.ini')
        if not env:
            db_env = ''
        else:
            db_env = env
        sec = 'db_{0}'.format(db_env)
        self.db_host = cf.get(sec, 'host')
        self.db_port = cf.getint(sec, 'port')
        self.db_user = cf.get(sec, 'user')
        self.db_pwd = cf.get(sec, 'password')
        self.db_name = cf.get(sec,'db_name')
        self.db_clientflag = cf.get(sec,'client_flag')
        self._connect = pymysql.connect(host=self.db_host, port=int(self.db_port), user=self.db_user, password=self.db_pwd, charset='utf8',db=self.db_name, init_command='set names utf8')
        
    def queryall(self, sql, params=None):
        cursor = self._connect.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            result = cursor.fetchall()
        finally:
            cursor.close()
        return result
    
    def update(self, sql, params=None):
        cursor = self._connect.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            self._connect.commit()
            result = cursor.rowcount
        finally:
            cursor.close()
        return result
            
    def close(self):
        if self._connect:
            self._connect.close()
            
    def get_mysql_conn(env=None):
        return MySqlConnector(env)