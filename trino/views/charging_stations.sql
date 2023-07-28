--- https://geoportal.freiburg.de/wfs/gdm_ls_moovility/gdm_ls_moovility?request=getfeature&service=wfs&version=1.1.0&typename=ms:ladesaeulen_raw&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326
create or replace view staging.smart_city.charging_stations as
with stations_json as (
select
	cast(json_parse(json_query(data,
	'lax $.features[*]' with array WRAPPER)) as array(row(
		properties row(
			lades_id bigint,
			last_updated varchar,
		    address varchar,
			postal_code varchar,
			city varchar,
			op_name varchar,
			op_website varchar,
			op_phonenumber varchar,
			evses array(row(uid varchar,
	evse_id varchar,
	status varchar,
	capabilities array(varchar),
	connectors array(row(id bigint,
	standard varchar,
	format varchar,
	power_type varchar,
	voltage bigint,
	amperage bigint,
	last_updated varchar,
	gdm_kilowatt varchar)),
	CIT_stateID bigint,
	last_updated varchar,
	gdm_dt_status varchar,
	gdm_capabilities varchar,
	gdm_standard varchar)),
			gdm_n_evenses bigint,
			gdm_n_available bigint,
			gdm_n_charging bigint,
			gdm_n_outoforder bigint,
			gdm_n_unknown bigint
		),
		geometry row (
		  type varchar,
		  coordinates array(double)
		  )
		)
	)) as stations
from
	storage.raw."https://geoportal.freiburg.de/wfs/gdm_ls_moovility/gdm_ls_moovility?request=getfeature&service=wfs&version=1.1.0&typename=ms:ladesaeulen_raw&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326"
)
select
    properties.lades_id as lades_id,
    properties.last_updated as last_updated,
    properties.address as address,
    properties.postal_code as postal_code,
    properties.city as city,
    properties.op_name as op_name,
    properties.op_website as op_website,
    properties.op_phonenumber as op_phonenumber,
    properties.gdm_n_evenses as gdm_n_evenses,
    properties.gdm_n_available as gdm_n_available,
    properties.gdm_n_charging as gdm_n_charging,
    properties.gdm_n_outoforder as gdm_n_outoforder,
    properties.gdm_n_unknown as gdm_n_unknown,
    geometry.coordinates[2] as latitude,
    geometry.coordinates[1] as longitude,
    ev.uid,
    ev.status,
    ev.evse_id
from
    stations_json
        cross join unnest(stations)
        cross join unnest(properties.evses) as ev;
