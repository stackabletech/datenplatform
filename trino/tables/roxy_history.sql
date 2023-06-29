CREATE TABLE lakehouse.smart_city.roxy_history
(
    timestamp timestamp(6) with time zone,
    id        varchar,
    reserved  varchar,
    latitude  double,
    longitude double
)
    WITH (
        format = 'ORC',
        format_version = 2,
        location = 's3a://stackable-freiburg-lakehouse/smart-city/roxy_history-46b1e0e34f744d9796105c8a9025d4b5'
        );