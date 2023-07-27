CREATE OR REPLACE VIEW staging.platform.roxy AS
WITH json AS (SELECT CAST(
                             json_parse(JSON_QUERY(data FORMAT JSON, 'lax $.features[*]' WITH UNCONDITIONAL ARRAY WRAPPER NULL ON EMPTY NULL ON ERROR)) AS array
                             (ROW(properties ROW(id varchar, reserved varchar), geometry ROW(type varchar, coordinates array(double))))) roxies
              FROM storage.raw."https://geoportal.freiburg.de/wfs/gdm_sharing/gdm_sharing?request=GetFeature&service=WFS&version=1.1.0&typeName=:roxy&outputFormat=application%2Fjson%3B%20subtype%3Dgeojson%3B%20charset%3Dutf-8&SRSNAME=urn:ogc:def:crs:EPSG::4326")
SELECT properties.id                                              id
     , properties.reserved                                        reserved
     , geometry.coordinates[2]                                    latitude
     , geometry.coordinates[1]                                    longitude
     , ST_Point(geometry.coordinates[1], geometry.coordinates[2]) coordinates
FROM (json
    CROSS JOIN UNNEST(roxies));
