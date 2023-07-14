CREATE VIEW staging.platform.yoio AS
WITH json AS (SELECT CAST(
                             json_parse(JSON_QUERY(data FORMAT JSON, 'lax $.features[*]' WITH UNCONDITIONAL ARRAY WRAPPER NULL ON EMPTY NULL ON ERROR)) AS array
                             (ROW(properties ROW(nr varchar, current_range_meters bigint, rental_uri_android varchar, rental_uri_ios varchar, rental_uri_web varchar), geometry ROW(type varchar, coordinates array(double))))) yoio
              FROM storage.raw."https://geoportal.freiburg.de/wfs/gdm_sharing/gdm_sharing?request=GetFeature&service=WFS&version=1.1.0&typeName=:yoio&outputFormat=application%2Fjson%3B%20subtype%3Dgeojson%3B%20charset%3Dutf-8&SRSNAME=urn:ogc:def:crs:EPSG::4326")
SELECT properties.nr                                              nr
     , properties.current_range_meters                            current_range_meters
     , properties.rental_uri_android                              rental_uri_android
     , properties.rental_uri_ios                                  rental_uri_ios
     , properties.rental_uri_web                                  rental_uri_web
     , geometry.coordinates[2]                                    latitude
     , geometry.coordinates[1]                                    longitude
     , ST_Point(geometry.coordinates[1], geometry.coordinates[2]) coordinates
FROM (json
    CROSS JOIN UNNEST(yoio))