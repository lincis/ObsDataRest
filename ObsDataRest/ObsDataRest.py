import configparser
import os
from .db import get_conn

from flask import Flask, request, jsonify, g
from flask_restful import Resource, Api
import logging

app = Flask(__name__)
api = Api(app)

mypath = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(mypath,"ObsDataRest.cfg"))

db_file = os.path.join(mypath,config["database"]["path"])

def init_db(path = None):
    if not path:
        path = getattr(g, "db_file", db_file)
    with app.app_context():
        conn, cursor = get_conn(path, True)
        with app.open_resource('struct.sql', mode='r') as f:
            cursor.executescript(f.read())
        conn.commit()
    g.db_file = path

logging.basicConfig(
    filename = '%s.log' % __name__,
    level=logging.DEBUG,
    format='%(asctime)s %(message)s',
)

class _ODRBase(Resource):
    def __init__(self):
        self.conn, self.cursor = get_conn(getattr(g, "db_file", db_file))
        super(_ODRBase, self).__init__()

class  DataSources(_ODRBase):
    def get(self, source_id = None):
        logging.info("%s.%s(%s)" % (self.__class__.__name__, "get", source_id))
        try:
            if source_id:
                query = self.cursor.execute('select * from DataSources where DataSourceID = ?', (source_id,))
                rv = query.fetchone()
            else:
                query = self.cursor.execute('select * from DataSources')
                rv = query.fetchall()
            logging.info("%s.%s() = %s" % (self.__class__.__name__, "get", rv))
            return{'DataSources': rv}
        except:
            logging.error("%s.%s() failed" % (self.__class__.__name__, "get"), exc_info = True)
            raise

    def post(self, source_id):
        logging.info("%s.%s(%s, %s)" % (self.__class__.__name__, "post", source_id, request.json))
        try:
            name = request.json['Name']
            desc = request.json['Description']
            self.cursor.execute('insert into DataSources values (?,?,?)',(source_id, name, desc))
            self.conn.commit()
        except:
            logging.error("%s.%s() failed" % (self.__class__.__name__, "post"), exc_info = True)
            raise

    def delete(self, source_id):
        logging.info("%s.%s(%s)" % (self.__class__.__name__, "delete", source_id))
        try:
            self.cursor.execute('delete from DataSources where DataSourceID = ?',(source_id,))
            self.conn.commit()
        except:
            logging.error("%s.%s() failed" % (self.__class__.__name__, "delete"), exc_info = True)
            raise

class DataTypes(_ODRBase):
    def get(self, type_id = None):
        logging.info("%s.%s(%s)" % (self.__class__.__name__, "get", type_id))
        try:
            if type_id:
                query = self.cursor.execute('select * from DataTypes where DataTypeID = ?', (type_id,))
                rv = query.fetchone()
            else:
                query = self.cursor.execute('select * from DataTypes')
                rv = query.fetchall()
            logging.info("%s.%s() = %s" % (self.__class__.__name__, "get", rv))
            return{'DataTypes': rv}
        except:
            logging.error("%s.%s() failed" % (self.__class__.__name__, "get"), exc_info = True)
            raise

    def put(self, type_id = None):
        logging.info("%s.%s(%s, %s)" % (self.__class__.__name__, "put", type_id, request.json))
        if not type_id:
            return '', 405
        try:
            name = request.json['Name']
            desc = request.json['Description']
            units = request.json['Units']
            query = self.cursor.execute('select DataTypeID from DataTypes where DataTypeID = ?', (type_id,))
            if len(query.fetchall()):
                self.cursor.execute('update DataTypes set Name = ?, Description = ?, Units = ? where DataTypeID = ?',(name, desc, units, type_id))
                rc = 201
            else:
                self.cursor.execute('insert into DataTypes values (?,?,?,?)',(type_id, name, desc, units))
                rc = 200
            self.conn.commit()
        except:
            logging.error("%s.%s() failed" % (self.__class__.__name__, "put"), exc_info = True)
            raise
        return request.json, rc

    def delete(self, type_id):
        logging.info("%s.%s(%s)" % (self.__class__.__name__, "delete", type_id))
        try:
            self.cursor.execute('delete from DataTypes where DataTypeID = ?',(type_id,))
            self.conn.commit()
        except:
            logging.error("%s.%s() failed" % (self.__class__.__name__, "delete"), exc_info = True)
            raise

api.add_resource(DataSources,
        '/sources/<source_id>',
        '/sources/'
    )
api.add_resource(DataTypes,
        '/types/<type_id>',
        '/types/'
    )
