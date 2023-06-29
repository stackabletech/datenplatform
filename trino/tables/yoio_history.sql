CREATE TABLE lakehouse.smart_city.yoio_history
(
    timestamp            timestamp(6) with time zone,
    nr                   varchar,
    current_range_meters bigint,
    rental_uri_android   varchar,
    rental_uri_ios       varchar,
    rental_uri_web       varchar,
    latitude             double,
    longitude            double
)
    WITH (
        format = 'ORC',
        format_version = 2,
        location = 's3a://stackable-freiburg-lakehouse/smart-city/yoio_history-4621cfebb26045c7928f0925917e436b'
        );