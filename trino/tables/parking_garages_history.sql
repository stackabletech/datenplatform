CREATE TABLE lakehouse.platform.parking_garages_history
(
    obs_id     bigint,
    obs_parkid bigint,
    obs_state  bigint,
    obs_max    bigint,
    obs_free   bigint,
    obs_ts     timestamp(6),
    park_name  varchar,
    park_id    varchar,
    trend      bigint,
    prozent    bigint,
    park_url   varchar,
    park_zone  varchar,
    free_color varchar,
    status     bigint,
    latitude   double,
    longitude  double
);
