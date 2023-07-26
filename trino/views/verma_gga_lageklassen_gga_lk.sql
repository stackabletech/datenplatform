
create or REPLACE view staging.smart_city.verma_gga_lageklassen_gga_lk as
with json as (
select
	cast(
    json_parse(
       json_query(data,
	     'lax $.features[*]' with array WRAPPER)) as array(row(
	        properties row(
			 gid bigint,
			 objectid_1 bigint,
			 nutzung varchar,
			 gfz14_iii double, 
			 d_innenst varchar, 
			 stadtteil varchar,
			 geschosse varchar,
			 jahr bigint,
			 brwz_nr bigint,
			 brw bigint,
			 zustand varchar,
			 lk_mod varchar,
			 lk_text varchar,
			 brw16sg bigint
	 ),
	 geometry row(
		  type varchar,
		  coordinates array(array(array(double)))
		  )))) temp
from
	storage.raw."https://geoportal.freiburg.de/wfs/verma_gga/verma_gga_lageklassen?request=getfeature&service=wfs&version=2.0.0&typename=ms:gga_lk&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326")
select
    properties.gid id,
    properties.objectid_1 objectid_1,
    properties.nutzung nutzung,
    properties. gfz14_iii gfz14_iii,
    properties.d_innenst d_innenst,
    properties.stadtteil stadtteil,
    properties. geschosse geschosse,
    properties.jahr jahr,
    properties.brwz_nr brwz_nr,
    properties.brw brw,
    properties.zustand zustand,
    properties.lk_mod lk_mod,
    properties.lk_text lk_text,
    properties.brw16sg brw16sg,
    to_geometry(from_geojson_geometry(json_format(cast(geometry as json)))) as geometry,
    json_format(cast(geometry as json)) as geometry_geojson
from
    (json
        cross join unnest(temp));