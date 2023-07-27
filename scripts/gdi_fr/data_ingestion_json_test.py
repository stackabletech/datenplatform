# coding: utf-8
import ast
from io import StringIO

import geopandas as gpd
import pandas as pd
import requests
from sqlalchemy import create_engine
from sqlalchemy.sql import expression
from trino.sqlalchemy import URL

from scripts.dcat2trino import trino_connection


def cleanup_name(name):
    return str(name) \
        .replace(" ", "_") \
        .replace("(", "") \
        .replace(")", "") \
        .replace("-", "_") \
        .replace(",", "") \
        .replace(".", "") \
        .replace("\\", "") \
        .replace("/", "") \
        .lower() \
        .replace("ä", "ae") \
        .replace("ü", "ue") \
        .replace("ö", "oe") \
        .replace("ß", "ss")


urls = [
    "https://geoportal.freiburg.de/wfs/verma_gga/verma_gga_lageklassen?request=getfeature&service=wfs&version=2.0.0&typename=ms:gga_lk&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2023_flaechen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2023_grenzen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2022_flaechen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2022_grenzen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2020&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2019&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2018&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2016&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2014&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2012&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2010&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2008&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:punktraster_2008&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2008_b&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/vag_stops/vag_stops?request=getfeature&service=wfs&version=2.0.0&typename=ms:stops&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/vag_stops/vag_stops?request=getfeature&service=wfs&version=2.0.0&typename=ms:stops_master&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/vag_stops/vag_stops?request=getfeature&service=wfs&version=2.0.0&typename=ms:lines&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:fliessgew_o12&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:graeben&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:gew_kilometr&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:grundwasserflurabstand&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:grundwasserhochstand&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:hq100_typ2&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:schutz&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:hrbts&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:bruecke&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:schacht&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:fliess&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:flaeche&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:leitung&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/uwsa_oekol_stdplan/oekol_stdplan?request=getfeature&service=wfs&version=2.0.0&typename=ms:oekol_stdplan&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/stpla_satzung/stpla_satzung?request=getfeature&service=wfs&version=2.0.0&typename=ms:entwicklungssatzung&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/stpla_satzung/stpla_satzung?request=getfeature&service=wfs&version=2.0.0&typename=ms:erhaltungssatzung&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/stpla_satzung/stpla_satzung?request=getfeature&service=wfs&version=2.0.0&typename=ms:sanierungssatzung&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/stpla_satzung/stpla_satzung?request=getfeature&service=wfs&version=2.0.0&typename=ms:vorkaufssatzung&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/stav_strlex/stav_strlex?request=getfeature&service=wfs&version=2.0.0&typename=ms:strlex&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_winter/gut_winter?request=getfeature&service=wfs&version=2.0.0&typename=ms:strassen_winter&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_winter/gut_winter?request=getfeature&service=wfs&version=2.0.0&typename=ms:radwege_winter&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_winter/gut_winter?request=getfeature&service=wfs&version=2.0.0&typename=ms:gruen_winter&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_spielplatz/gut_spielplatz?request=getfeature&service=wfs&version=2.0.0&typename=ms:bolzplaetze&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_spielplatz/gut_spielplatz?request=getfeature&service=wfs&version=2.0.0&typename=ms:skateplaetze&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_spielplatz/gut_spielplatz?request=getfeature&service=wfs&version=2.0.0&typename=ms:spielplaetze&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn_nacht&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn_tag&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:strasse_nacht&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:strasse_tag&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn2010_tag&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn2010_nacht&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn2015_tag&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn2015_nacht&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_grillstellen/gut_grillstellen?request=getfeature&service=wfs&version=2.0.0&typename=ms:grillstellen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_grillstellen/gut_grillstellen?request=getfeature&service=wfs&version=2.0.0&typename=ms:grillzonen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_verkehrssensorik/gdm_verkehrssensorik?request=getfeature&service=wfs&version=2.0.0&typename=ms:ui_thermal&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_sharing/gdm_sharing?request=getfeature&service=wfs&version=2.0.0&typename=ms:frelo&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_sharing/gdm_sharing?request=getfeature&service=wfs&version=2.0.0&typename=ms:yoio&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_sharing/gdm_sharing?request=getfeature&service=wfs&version=2.0.0&typename=ms:roxy&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_sharing/gdm_sharing?request=getfeature&service=wfs&version=2.0.0&typename=ms:freib-e&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:parken&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:aussichtstuerme&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:forst&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:blitzer&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:brunnen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:camping&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:kulturdenkmal&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:feuerwehr&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:jugendtreffs&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:kirchen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:kita&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:krankenhaeuser&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:museen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:polizei&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:post&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:rastplaetze&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:ruinen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:schanzen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:taxi&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:funktuerme&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:tourist_info&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:wc&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:begegnung&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtteilzentren&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:windkraft&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:schulen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtverwaltung&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:grundschulen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_plz/gdm_plz?request=getfeature&service=wfs&version=2.0.0&typename=ms:plz_fr&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_ls_moovility/gdm_ls_moovility?request=getfeature&service=wfs&version=1.1.0&typename=ms:ladesaeulen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_ls_moovility/gdm_ls_moovility?request=getfeature&service=wfs&version=1.1.0&typename=ms:ladesaeulen_raw&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_gemarkung/gdm_gemarkung?request=getfeature&service=wfs&version=2.0.0&typename=ms:gemarkungen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_gemarkung/gdm_gemarkung?request=getfeature&service=wfs&version=2.0.0&typename=ms:gemarkungen_umr&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_fahrrad_stat/gdm_fahrrad_stat?request=getfeature&service=wfs&version=2.0.0&typename=ms:avs&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_fahrrad_stat/gdm_fahrrad_stat?request=getfeature&service=wfs&version=2.0.0&typename=ms:count_direction&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_fahrrad_stat/gdm_fahrrad_stat?request=getfeature&service=wfs&version=2.0.0&typename=ms:count_total&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_fahrrad_stat/gdm_fahrrad_stat?request=getfeature&service=wfs&version=2.0.0&typename=ms:rad_heatmap&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_address/gdm_address?request=getfeature&service=wfs&version=2.0.0&typename=ms:addresses&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_address/gdm_address?request=getfeature&service=wfs&version=2.0.0&typename=ms:addresses_streets&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/fa_befall/fa_befall?request=getfeature&service=wfs&version=2.0.0&typename=ms:befall&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/aki_kita/aki_kita?request=getfeature&service=wfs&version=2.0.0&typename=ms:kita_fritz&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/aki_kita/aki_kita?request=getfeature&service=wfs&version=2.0.0&typename=ms:kita_waldwaegen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/aki_kita/aki_kita?request=getfeature&service=wfs&version=2.0.0&typename=ms:okja&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak_test_alle?request=getfeature&service=wfs&version=2.0.0&typename=ms:evakuierungsradius&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak_test_alle?request=getfeature&service=wfs&version=2.0.0&typename=ms:geb_in_radius&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak_test_alle?request=getfeature&service=wfs&version=2.0.0&typename=ms:addr_in_radius&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak?request=getfeature&service=wfs&version=2.0.0&typename=ms:evakuierungsradius&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak?request=getfeature&service=wfs&version=2.0.0&typename=ms:geb_in_radius&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak?request=getfeature&service=wfs&version=2.0.0&typename=ms:addr_in_radius&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_flaeche&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_01&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_02&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_03&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_04&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_05&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_06&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_07&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_08&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_09&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_10&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_11&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_12&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_13&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_14&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_15&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_16&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_umrisse&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_standorte&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abi_gsb/abi_gsb?request=getfeature&service=wfs&version=2.0.0&typename=ms:grundschulbezirke&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abi_gsb/abi_gsb?request=getfeature&service=wfs&version=2.0.0&typename=ms:grundschulstandorte&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:baubloecke&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:statistische_bezirke&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtbezirke&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtteile&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtbereiche&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtteile_out&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gut_off_obj/komregie_strassen?request=getfeature&service=wfs&version=2.0.0&typename=ms:strassen&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?request=getfeature&service=wfs&version=2.0.0&typename=ms:pls&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?request=getfeature&service=wfs&version=2.0.0&typename=ms:pls_no_zone&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?request=getfeature&service=wfs&version=2.0.0&typename=ms:pls2&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326",
    "https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?request=getfeature&service=wfs&version=2.0.0&typename=ms:parkzonen_live&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326"

    # TODO: Die nachfolgenden liefern in keinem Format Daten. Laut Beschreibung sollten eigentlich XML oder GML/3.2.1 funktionieren
    # "https://geoportal.freiburg.de/wfs/stpla_bplan_verf/stpla_bplan_verf?request=getfeature&service=wfs&version=2.0.0&typename=ms:bplan_verf&outputformat=xml&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:begegnungsst&outputformat=geojson&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:beratung_aeltere&outputformat=geojson&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:pflegeeinrichtungen&outputformat=geojson&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:seniorenwohnanlagen&outputformat=geojson&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:wohnstift&outputformat=geojson&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:tagespflege&outputformat=geojson&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:pflegewohngruppe&outputformat=geojson&srsname=epsg:25832",
    # TODO: fehlerhafte Datei
    # "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:haltestellen&outputformat=geojson&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/verma_gga/verma_gga_lageklassen?request=getfeature&service=wfs&version=2.0.0&typename=ms:gga_lk_2022&outputformat=geojson&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:hinweis&outputformat=geojson&srsname=epsg:25832",
]
typemapping = {"object": "varchar", "int64": "bigint", "float64": "double", "geometry": "varchar", "datetime64[ns]": "varchar"}

engine = create_engine(
    URL(
        host=trino_connection.host,
        port=trino_connection.port,
        catalog=trino_connection.catalog,
        user=trino_connection.user,
        password=trino_connection.password
    ),
    connect_args={
        "verify": False
    }
)
connection = engine.connect()
typemapping = {"object": "varchar", "int64": "bigint", "float64": "double", "geometry": "varchar"}

for url in urls:
    print(url)
    r = requests.get(url)
    content = StringIO(r.content.decode('utf-8'))
    df_new = pd.DataFrame()

    try:
        gdf = gpd.read_file(content)
        df = pd.DataFrame(gdf)
        for col in df.columns:
            try:
                df[col] = df[col].apply(ast.literal_eval)
                s = df[col].explode()
                if len(s.apply(pd.Series).columns) > 1:
                    s = pd.concat([s, s.apply(pd.Series)], axis=1).drop(col, axis=1)
                    s = s.reset_index()
                    df_new = df_new.merge(s, how='left', left_on=df_new.index, right_on='index')
                else:
                    df_new[col] = df[col]
            except Exception as e:
                df_new[col] = df[col]
    except pd.errors.ParserError:
        print(url, 'Parse Error CSV')

    description_1 = url.split('?')[0].split('/')[-1]
    description_2 = url.split('typename=ms:')[-1].split('&')[0].replace('-', '_')
    sqlfile = f"sql/{description_1}_{description_2}.sql"
    with open(sqlfile, 'w') as writer:
        statement = f"create or REPLACE view staging.smart_city.{description_1}_{description_2} as\n"
        statement += "\twith json as (\n"
        statement += "\t\tselect\n"
        statement += "\t\tcast(\n"
        statement += "\t\tjson_parse(\n"
        statement += "\t\tjson_query(data,\n"
        statement += "\t\t'lax $.features[*]' with array WRAPPER)) as array(row(\n"
        statement += "\t\t\tproperties row(\n"
        sts = []
        for column in df_new.columns:
            if column != 'geometry':
                sts.append(f"\t\t\t\t{cleanup_name(column)} {typemapping.get(str(df_new.dtypes[column]), 'varchar')}")
        statement += ",\n".join(sts)
        statement += "\n"
        statement += "\t\t\t),\n"
        statement += "\t\t\tgeometry row(\n"
        statement += "\t\t\t\ttype varchar,\n"
        statement += "\t\t\t\tcoordinates array(array(array(double)))\n"
        statement += "\t\t)))) temp\n"
        statement += f"from storage.raw.\"{url}\")\n"
        statement += "select\n"

        sts = []
        for column in df_new.columns:
            if column != 'geometry':
                sts.append(f"\tproperties.{cleanup_name(column)} {cleanup_name(column)}")

        statement += ",\n".join(sts)
        statement += ",\n"
        statement += "\tto_geometry(from_geojson_geometry(json_format(cast(geometry as json)))) as geometry,\n"
        statement += "\tjson_format(cast(geometry as json)) as geometry_geojson,\n"
        statement += "\tjson_object(\'type\': \'Polygon\', \'geometry\': json_format(cast(geometry as json)) FORMAT JSON) as geometry_geojson2\n"
        statement += "from (json cross join unnest(temp))"
        writer.write(statement)

        try:
            connection.execute(expression.text(statement))
        except Exception as e:
            print(f"Failed to create table [{description_1}_{description_2}] due to [{e}]")
            continue
