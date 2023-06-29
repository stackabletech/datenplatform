CREATE TABLE lakehouse.smart_city.freibe_history
(
    id            varchar,
    fuellevel     bigint,
    vehicletypeid varchar,
    latitude      double,
    longitude     double
)
    WITH (
        format = 'ORC',
        format_version = 2,
        location = 's3a://stackable-freiburg-lakehouse/smart-city/freibe_history-756a19ab24ec4cbe8947054252bbb91b'
        );