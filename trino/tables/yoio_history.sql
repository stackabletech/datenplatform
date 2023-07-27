CREATE TABLE lakehouse.platform.yoio_history
(
    timestamp            timestamp(6) with time zone,
    nr                   varchar,
    current_range_meters bigint,
    rental_uri_android   varchar,
    rental_uri_ios       varchar,
    rental_uri_web       varchar,
    latitude             double,
    longitude            double
);
