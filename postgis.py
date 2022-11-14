#obsuga połączenia i zapisu działki w postgis

import geopandas as gpd
from sqlalchemy import create_engine

def connection(user, password, host, port, database):
   return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")

def wkt_to_postgis(connection, tab, teryt, geom):
   try:
      sql = f"INSERT INTO {tab} VALUES ('{teryt}','{geom}')"
      gpd.GeoDataFrame.from_postgis(sql, connection)
   except:
      pass

