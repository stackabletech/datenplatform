CREATE TABLE lakehouse.smart_city.frelo_history
(
    timestamp          timestamp(6) with time zone,
    longitude          double,
    latitude           double,
    name               varchar,
    address            varchar,
    free_bikes         bigint,
    free_space         bigint,
    free_special_space bigint,
    station_number     bigint,
    freloplus          boolean,
    free_cargo_bikes   bigint
)
    WITH (
        format = 'ORC',
        format_version = 2,
        location = 's3a://stackable-freiburg-lakehouse/smart-city/bikes_history-5bb7601001724a8c9149801e30cdbcc1'
        );