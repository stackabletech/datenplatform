CREATE VIEW staging.smart_city.freibe AS
WITH json AS (SELECT CAST(
                             json_parse(JSON_QUERY(data FORMAT JSON, 'lax $.features[*]' WITH UNCONDITIONAL ARRAY WRAPPER NULL ON EMPTY NULL ON ERROR)) AS array
                             (ROW(properties ROW(id varchar, fuelLevel bigint, vehicleTypeId varchar), geometry ROW(type varchar, coordinates array(double))))) freibe
              FROM storage.raw."https://geoportal.freiburg.de/wfs/gdm_sharing/gdm_sharing?request=GetFeature&service=WFS&version=1.1.0&typeName=:freib-e&outputFormat=application%2Fjson%3B%20subtype%3Dgeojson%3B%20charset%3Dutf-8&SRSNAME=urn:ogc:def:crs:EPSG::4326")
SELECT properties.id            id
     , properties.fuelLevel     fuelLevel
     , properties.vehicleTypeId vehicleTypeId
     , geometry.coordinates[2]  latitude
     , geometry.coordinates[1]  longitude
FROM (json
    CROSS JOIN UNNEST(freibe));