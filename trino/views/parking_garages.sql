CREATE VIEW staging.platform.parking_garages SECURITY DEFINER AS
    WITH
    json AS (
    SELECT CAST (json_parse(JSON_QUERY(data FORMAT JSON, 'lax $.features[*]' WITH UNCONDITIONAL ARRAY WRAPPER NULL ON EMPTY NULL ON ERROR
)
) AS array(ROW (properties ROW (obs_id bigint, obs_parkid bigint, obs_state bigint, obs_max bigint, obs_free bigint, obs_ts varchar, park_name varchar, park_id varchar, trend bigint, prozent bigint, park_url varchar, park_zone varchar, free_color varchar, status bigint
), geometry ROW (type varchar, coordinates array(double
)
)
)
)
) garages
    FROM
    storage.raw."https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?request=GetFeature&service=WFS&version=1.1.0&typeName=:pls&outputFormat=application%2Fjson%3B%20subtype%3Dgeojson%3B%20charset%3Dutf-8&SRSNAME=urn:ogc:def:crs:EPSG::4326"
)
SELECT properties.obs_id                                          obs_id
     , properties.obs_parkid                                      obs_parkid
     , properties.obs_state                                       obs_state
     , properties.obs_max                                         obs_max
     , properties.obs_free                                        obs_free
     , CAST(properties.obs_ts AS timestamp)                       obs_ts
     , properties.park_name                                       park_name
     , properties.park_id                                         park_id
     , properties.trend                                           trend
     , properties.prozent                                         prozent
     , properties.park_url                                        park_url
     , properties.park_zone                                       park_zone
     , properties.free_color                                      free_color
     , properties.status                                          status
     , geometry.coordinates[2]                                    latitude
     , geometry.coordinates[1]                                    longitude
     , ST_Point(geometry.coordinates[1], geometry.coordinates[2]) coordinates
FROM (json
    CROSS JOIN UNNEST(garages));