import configparser
from sqlalchemy import create_engine

config = configparser.ConfigParser()
config.read('configdb/config.txt')

engine = create_engine(config.get('database', 'con'))