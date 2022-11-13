import geopandas as gpd
from sqlalchemy import create_engine

def connection(user, password, host, port, database):
   return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")

def wkt_to_postgis(database, tab, teryt, geom):
    sql = f"INSERT INTO {tab} VALUES ('{teryt}','{geom}')"
    gpd.GeoDataFrame.from_postgis(sql, database)


bazaTest = connection('####', '######', '###.###.###.##', '####', '#####')

teryt ='260412_5.0004.907'
wkt = 'POLYGON((610997.122424037 325258.456388454,610910.331368991 325241.500130218,610908.730033348 325241.186840794,610824.471558067 325230.4083874,610650.793474912 325215.941018176,610610.199624444 325224.761657582,610568.318487765 325233.857432522,610531.536294924 325241.861292904,610437.122639231 325257.194981302,610386.267019931 325265.388035426,610332.500052662 325265.143322592,610284.004722388 325268.880765312,610273.497118613 325271.056206804,610199.741099296 325286.388793097,610148.442214858 325124.320269848,610154.541811906 325127.264947028,610148.46286146 325098.423935958,610354.130242333 325015.558329206,610776.029208539 324845.573064647,610922.235745126 324786.665583222,610967.625634704 324927.667069406,610993.417539518 325119.682392983,610997.122424037 325258.456388454))'
wkt_to_postgis(bazaTest, 'plots', teryt, wkt)

# sql = "SELECT * from public.zloza_lafarge"
# zloza = gpd.GeoDataFrame.from_postgis(sql,engine,geom_col='geom')
# print(zloza.head())

