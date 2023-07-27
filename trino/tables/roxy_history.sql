CREATE TABLE lakehouse.platform.roxy_history
(
    timestamp timestamp(6) with time zone,
    id        varchar,
    reserved  varchar,
    latitude  double,
    longitude double
);
