CREATE OR REPLACE VIEW staging.platform.frelo AS
WITH bikes AS (SELECT *
               FROM storage.csv."https://geoportal.freiburg.de/wfs/gdm_sharing/gdm_sharing?request=GetFeature&service=WFS&version=1.1.0&typeName=:frelo&outputFormat=text%2Fcsv&SRSNAME=urn:ogc:def:crs:EPSG::4326")
SELECT ST_GeometryFromText(trim(LEADING '"' FROM trim(TRAILING '"' FROM wkt)))                                              location
     , ST_X(ST_GeometryFromText(trim(LEADING '"' FROM trim(TRAILING '"' FROM wkt))))                                        longitude
     , ST_Y(ST_GeometryFromText(trim(LEADING '"' FROM trim(TRAILING '"' FROM wkt))))                                        latitude
     , to_geojson_geometry(to_spherical_geography(ST_GeometryFromText(trim(LEADING '"' FROM trim(TRAILING '"' FROM wkt))))) location_geo_json
     , name
     , address
     , CAST(trim(LEADING '"' FROM trim(TRAILING '"' FROM freie_raeder)) AS bigint)                                          free_bikes
     , CAST(trim(LEADING '"' FROM trim(TRAILING '"' FROM freie_plaetze)) AS bigint)                                         free_space
     , CAST(trim(LEADING '"' FROM trim(TRAILING '"' FROM freie_spezialplaetze)) AS bigint)                                  free_special_space
     , CAST(trim(LEADING '"' FROM trim(TRAILING '"' FROM station_nr)) AS bigint)                                            station_number
     , CAST(einzelrad AS boolean)                                                                                           freloplus
     , CAST(trim(LEADING '"' FROM trim(TRAILING '"' FROM freloplus)) AS bigint)                                             free_cargo_bikes
FROM bikes;
