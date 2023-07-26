# coding: utf-8
import ast
import json
from io import StringIO

import requests
import pandas as pd
import geopandas as gpd
from trino.sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.sql import expression

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
    "https://geoportal.freiburg.de/wfs/verma_gga/verma_gga_lageklassen?request=getfeature&service=wfs&version=2.0.0&typename=ms:gga_lk&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_gga/verma_gga_lageklassen?request=getfeature&service=wfs&version=2.0.0&typename=ms:gga_lk_2022&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2023_flaechen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2023_grenzen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2022_flaechen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2022_grenzen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2020&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2019&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2018&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2016&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2014&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:hinweis&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2012&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2010&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2008&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:punktraster_2008&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2008_b&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/vag_stops/vag_stops?request=getfeature&service=wfs&version=2.0.0&typename=ms:stops&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/vag_stops/vag_stops?request=getfeature&service=wfs&version=2.0.0&typename=ms:stops_master&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/vag_stops/vag_stops?request=getfeature&service=wfs&version=2.0.0&typename=ms:lines&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:fliessgew_o12&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:graeben&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:gew_kilometr&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:grundwasserflurabstand&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:grundwasserhochstand&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:hq100_typ2&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:schutz&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:hrbts&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:bruecke&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:schacht&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:fliess&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:flaeche&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:leitung&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_oekol_stdplan/oekol_stdplan?request=getfeature&service=wfs&version=2.0.0&typename=ms:oekol_stdplan&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/stpla_satzung/stpla_satzung?request=getfeature&service=wfs&version=2.0.0&typename=ms:entwicklungssatzung&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/stpla_satzung/stpla_satzung?request=getfeature&service=wfs&version=2.0.0&typename=ms:erhaltungssatzung&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/stpla_satzung/stpla_satzung?request=getfeature&service=wfs&version=2.0.0&typename=ms:sanierungssatzung&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/stpla_satzung/stpla_satzung?request=getfeature&service=wfs&version=2.0.0&typename=ms:vorkaufssatzung&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/stav_strlex/stav_strlex?request=getfeature&service=wfs&version=2.0.0&typename=ms:strlex&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_winter/gut_winter?request=getfeature&service=wfs&version=2.0.0&typename=ms:strassen_winter&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_winter/gut_winter?request=getfeature&service=wfs&version=2.0.0&typename=ms:radwege_winter&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_winter/gut_winter?request=getfeature&service=wfs&version=2.0.0&typename=ms:gruen_winter&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_spielplatz/gut_spielplatz?request=getfeature&service=wfs&version=2.0.0&typename=ms:bolzplaetze&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_spielplatz/gut_spielplatz?request=getfeature&service=wfs&version=2.0.0&typename=ms:skateplaetze&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_spielplatz/gut_spielplatz?request=getfeature&service=wfs&version=2.0.0&typename=ms:spielplaetze&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn_nacht&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn_tag&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:strasse_nacht&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:strasse_tag&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn2010_tag&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn2010_nacht&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn2015_tag&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn2015_nacht&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_grillstellen/gut_grillstellen?request=getfeature&service=wfs&version=2.0.0&typename=ms:grillstellen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_grillstellen/gut_grillstellen?request=getfeature&service=wfs&version=2.0.0&typename=ms:grillzonen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_verkehrssensorik/gdm_verkehrssensorik?request=getfeature&service=wfs&version=2.0.0&typename=ms:ui_thermal&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_sharing/gdm_sharing?request=getfeature&service=wfs&version=2.0.0&typename=ms:frelo&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_sharing/gdm_sharing?request=getfeature&service=wfs&version=2.0.0&typename=ms:yoio&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_sharing/gdm_sharing?request=getfeature&service=wfs&version=2.0.0&typename=ms:roxy&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_sharing/gdm_sharing?request=getfeature&service=wfs&version=2.0.0&typename=ms:freib-e&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:parken&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:aussichtstuerme&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:forst&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:blitzer&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:brunnen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:camping&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:kulturdenkmal&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:feuerwehr&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:jugendtreffs&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:kirchen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:kita&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:krankenhaeuser&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:museen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:polizei&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:post&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:rastplaetze&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:ruinen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:schanzen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:taxi&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:funktuerme&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:tourist_info&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:wc&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:begegnung&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtteilzentren&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:windkraft&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:schulen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtverwaltung&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:haltestellen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:grundschulen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_plz/gdm_plz?request=getfeature&service=wfs&version=2.0.0&typename=ms:plz_fr&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_ls_moovility/gdm_ls_moovility?request=getfeature&service=wfs&version=1.1.0&typename=ms:ladesaeulen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_ls_moovility/gdm_ls_moovility?request=getfeature&service=wfs&version=1.1.0&typename=ms:ladesaeulen_raw&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_gemarkung/gdm_gemarkung?request=getfeature&service=wfs&version=2.0.0&typename=ms:gemarkungen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_gemarkung/gdm_gemarkung?request=getfeature&service=wfs&version=2.0.0&typename=ms:gemarkungen_umr&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_fahrrad_stat/gdm_fahrrad_stat?request=getfeature&service=wfs&version=2.0.0&typename=ms:avs&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_fahrrad_stat/gdm_fahrrad_stat?request=getfeature&service=wfs&version=2.0.0&typename=ms:count_direction&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_fahrrad_stat/gdm_fahrrad_stat?request=getfeature&service=wfs&version=2.0.0&typename=ms:count_total&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_fahrrad_stat/gdm_fahrrad_stat?request=getfeature&service=wfs&version=2.0.0&typename=ms:rad_heatmap&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_address/gdm_address?REQUEST=GetFeature&SRSNAME=EPSG:25832&SERVICE=WFS&VERSION=2.0.0&TYPENAMES=addresses&outputformat=geojson",
    "https://geoportal.freiburg.de/wfs/gdm_address/gdm_address?request=getfeature&service=wfs&version=2.0.0&typename=ms:addresses_streets&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/fa_befall/fa_befall?request=getfeature&service=wfs&version=2.0.0&typename=ms:befall&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/aki_kita/aki_kita?request=getfeature&service=wfs&version=2.0.0&typename=ms:kita_fritz&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/aki_kita/aki_kita?request=getfeature&service=wfs&version=2.0.0&typename=ms:kita_waldwaegen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/aki_kita/aki_kita?request=getfeature&service=wfs&version=2.0.0&typename=ms:okja&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak_test_alle?request=getfeature&service=wfs&version=2.0.0&typename=ms:evakuierungsradius&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak_test_alle?request=getfeature&service=wfs&version=2.0.0&typename=ms:geb_in_radius&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak_test_alle?request=getfeature&service=wfs&version=2.0.0&typename=ms:addr_in_radius&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak?request=getfeature&service=wfs&version=2.0.0&typename=ms:evakuierungsradius&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak?request=getfeature&service=wfs&version=2.0.0&typename=ms:geb_in_radius&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak?request=getfeature&service=wfs&version=2.0.0&typename=ms:addr_in_radius&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_flaeche&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_01&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_02&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_03&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_04&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_05&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_06&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_07&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_08&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_09&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_10&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_11&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_12&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_13&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_14&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_15&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_16&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_umrisse&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_standorte&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abi_gsb/abi_gsb?request=getfeature&service=wfs&version=2.0.0&typename=ms:grundschulbezirke&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abi_gsb/abi_gsb?request=getfeature&service=wfs&version=2.0.0&typename=ms:grundschulstandorte&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:baubloecke&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:statistische_bezirke&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtbezirke&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtteile&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtbereiche&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtteile_out&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_off_obj/komregie_strassen?request=getfeature&service=wfs&version=2.0.0&typename=ms:strassen&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?request=getfeature&service=wfs&version=2.0.0&typename=ms:pls&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?request=getfeature&service=wfs&version=2.0.0&typename=ms:pls_no_zone&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?request=getfeature&service=wfs&version=2.0.0&typename=ms:pls2&outputformat=geojson&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?request=getfeature&service=wfs&version=2.0.0&typename=ms:parkzonen_live&outputformat=geojson&srsname=epsg:25832"
    # TODO: Die nachfolgenden liefern in keinem Format Daten. Laut Beschreibung sollten eigentlich XML oder GML/3.2.1 funktionieren
    # "https://geoportal.freiburg.de/wfs/stpla_bplan_verf/stpla_bplan_verf?request=getfeature&service=wfs&version=2.0.0&typename=ms:bplan_verf&outputformat=xml&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:begegnungsst&outputformat=geojson&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:beratung_aeltere&outputformat=geojson&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:pflegeeinrichtungen&outputformat=geojson&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:seniorenwohnanlagen&outputformat=geojson&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:wohnstift&outputformat=geojson&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:tagespflege&outputformat=geojson&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:pflegewohngruppe&outputformat=geojson&srsname=epsg:25832",
]

# engine = create_engine(
#     URL(
#         host=trino_connection.host,
#         port=trino_connection.port,
#         catalog=trino_connection.catalog,
#         user=trino_connection.user,
#         password=trino_connection.password
#     ),
#     connect_args={
#         "verify": False
#     }
# )
# connection = engine.connect()
# typemapping = {"object": "varchar", "int64": "bigint", "float64": "double"}

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

    print(df_new)
    description_1 = url.split('?')[0].split('/')[-1]
    description_2 = url.split('typename=ms:')[-1].split('&')[0]
    sqlfile = f"sql/{description_1}_{description_2}.sql"
    # with open(sqlfile, 'w') as writer:
    #     statement = f"CREATE or REPLACE VIEW staging.smart_city.{description_1}_{description_2} AS\n"
    #     statement += f"WITH temp AS (SELECT *\n"
    #     statement += f"\tFROM storage.csv.\"{row.downloadurl}\")\n"
    #     statement += f"SELECT\n"
    #     for column in range(len(df.columns)):
    #         statement += f"\tCAST(trim(LEADING '\"' FROM trim(TRAILING '\"' FROM \"{df.columns[column]}\")) AS {typemapping[str(df.dtypes[column])]}) {cleanup_name(df.columns[column])}"
    #         if column < len(df.columns) - 1:
    #             statement += ",\n"
    #         else:
    #             statement += "\n"
    #     statement += f"FROM temp\n"
    #     writer.write(statement, ";")
    #
    #     try:
    #         connection.execute(expression.text(statement))
    #     except Exception as e:
    #         print(f"Failed to create table [{description_1}_{description_2}] due to [{e}]")
    #         continue
