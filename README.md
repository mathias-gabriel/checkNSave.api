
shp2pgsql -I -s 4326 defibrillateurs-issy-les-moulineaux.shp FRANCE_issy-les-moulineaux_defibrillateurs | psql -U postgres -h localhost -d postgres


