CREATE TABLE lakehouse.platform.freibe_history (
    id              varchar,
    ts              timestamp(6),
    fuel_level      bigint,
    vehicle_type_id varchar,
    latitude        double,
    longitude       double
);
