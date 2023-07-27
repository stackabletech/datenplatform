CREATE TABLE lakehouse.platform.frelo_history
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
);
