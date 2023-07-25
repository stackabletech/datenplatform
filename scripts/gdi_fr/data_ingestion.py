# coding: utf-8
import ast
import json
from io import StringIO

import requests
import pandas as pd
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
    "https://geoportal.freiburg.de/wfs/verma_gga/verma_gga_lageklassen?request=getfeature&service=wfs&version=2.0.0&typename=ms:gga_lk&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_gga/verma_gga_lageklassen?request=getfeature&service=wfs&version=2.0.0&typename=ms:gga_lk_2022&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2023_flaechen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2023_grenzen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2022_flaechen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2022_grenzen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2020&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2019&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2018&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2016&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2014&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:hinweis&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2012&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2010&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2008&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:punktraster_2008&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/verma_brw/verma_brw?request=getfeature&service=wfs&version=2.0.0&typename=ms:zonen_2008_b&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/vag_stops/vag_stops?request=getfeature&service=wfs&version=2.0.0&typename=ms:stops&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/vag_stops/vag_stops?request=getfeature&service=wfs&version=2.0.0&typename=ms:stops_master&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/vag_stops/vag_stops?request=getfeature&service=wfs&version=2.0.0&typename=ms:lines&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:fliessgew_o12&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:graeben&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:gew_kilometr&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:grundwasserflurabstand&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:grundwasserhochstand&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:hq100_typ2&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:schutz&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:hrbts&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:bruecke&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:schacht&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:fliess&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:flaeche&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_wasser/uwsa_wasser?request=getfeature&service=wfs&version=2.0.0&typename=ms:leitung&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/uwsa_oekol_stdplan/oekol_stdplan?request=getfeature&service=wfs&version=2.0.0&typename=ms:oekol_stdplan&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/stpla_satzung/stpla_satzung?request=getfeature&service=wfs&version=2.0.0&typename=ms:entwicklungssatzung&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/stpla_satzung/stpla_satzung?request=getfeature&service=wfs&version=2.0.0&typename=ms:erhaltungssatzung&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/stpla_satzung/stpla_satzung?request=getfeature&service=wfs&version=2.0.0&typename=ms:sanierungssatzung&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/stpla_satzung/stpla_satzung?request=getfeature&service=wfs&version=2.0.0&typename=ms:vorkaufssatzung&outputformat=csv&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/stpla_bplan_verf/stpla_bplan_verf?request=getfeature&service=wfs&version=2.0.0&typename=ms:bplan_verf&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/stav_strlex/stav_strlex?request=getfeature&service=wfs&version=2.0.0&typename=ms:strlex&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_winter/gut_winter?request=getfeature&service=wfs&version=2.0.0&typename=ms:strassen_winter&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_winter/gut_winter?request=getfeature&service=wfs&version=2.0.0&typename=ms:radwege_winter&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_winter/gut_winter?request=getfeature&service=wfs&version=2.0.0&typename=ms:gruen_winter&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_spielplatz/gut_spielplatz?request=getfeature&service=wfs&version=2.0.0&typename=ms:bolzplaetze&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_spielplatz/gut_spielplatz?request=getfeature&service=wfs&version=2.0.0&typename=ms:skateplaetze&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_spielplatz/gut_spielplatz?request=getfeature&service=wfs&version=2.0.0&typename=ms:spielplaetze&outputformat=csv&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/gut_off_obj/komregie_strassen?request=getfeature&service=wfs&version=2.0.0&typename=ms:strassen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn_nacht&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn_tag&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:strasse_nacht&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:strasse_tag&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn2010_tag&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn2010_nacht&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn2015_tag&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_laerm/gut_laerm?request=getfeature&service=wfs&version=2.0.0&typename=ms:bahn2015_nacht&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_grillstellen/gut_grillstellen?request=getfeature&service=wfs&version=2.0.0&typename=ms:grillstellen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gut_grillstellen/gut_grillstellen?request=getfeature&service=wfs&version=2.0.0&typename=ms:grillzonen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_verkehrssensorik/gdm_verkehrssensorik?request=getfeature&service=wfs&version=2.0.0&typename=ms:ui_thermal&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_sharing/gdm_sharing?request=getfeature&service=wfs&version=2.0.0&typename=ms:frelo&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_sharing/gdm_sharing?request=getfeature&service=wfs&version=2.0.0&typename=ms:yoio&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_sharing/gdm_sharing?request=getfeature&service=wfs&version=2.0.0&typename=ms:roxy&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_sharing/gdm_sharing?request=getfeature&service=wfs&version=2.0.0&typename=ms:freib-e&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:parken&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:aussichtstuerme&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:forst&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:blitzer&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:brunnen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:camping&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:kulturdenkmal&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:feuerwehr&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:jugendtreffs&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:kirchen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:kita&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:krankenhaeuser&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:museen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:polizei&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:post&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:rastplaetze&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:ruinen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:schanzen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:taxi&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:funktuerme&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:tourist_info&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:wc&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:begegnung&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtteilzentren&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:windkraft&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:schulen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtverwaltung&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:haltestellen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_poi/gdm_poi?request=getfeature&service=wfs&version=2.0.0&typename=ms:grundschulen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_plz/gdm_plz?request=getfeature&service=wfs&version=2.0.0&typename=ms:plz_fr&outputformat=csv&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?request=getfeature&service=wfs&version=2.0.0&typename=ms:pls&outputformat=csv&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?request=getfeature&service=wfs&version=2.0.0&typename=ms:pls_no_zone&outputformat=csv&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?request=getfeature&service=wfs&version=2.0.0&typename=ms:pls2&outputformat=csv&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?request=getfeature&service=wfs&version=2.0.0&typename=ms:parkzonen_live&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_ls_moovility/gdm_ls_moovility?request=getfeature&service=wfs&version=1.1.0&typename=ms:ladesaeulen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_ls_moovility/gdm_ls_moovility?request=getfeature&service=wfs&version=1.1.0&typename=ms:ladesaeulen_raw&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_gemarkung/gdm_gemarkung?request=getfeature&service=wfs&version=2.0.0&typename=ms:gemarkungen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_gemarkung/gdm_gemarkung?request=getfeature&service=wfs&version=2.0.0&typename=ms:gemarkungen_umr&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_fahrrad_stat/gdm_fahrrad_stat?request=getfeature&service=wfs&version=2.0.0&typename=ms:avs&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_fahrrad_stat/gdm_fahrrad_stat?request=getfeature&service=wfs&version=2.0.0&typename=ms:count_direction&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_fahrrad_stat/gdm_fahrrad_stat?request=getfeature&service=wfs&version=2.0.0&typename=ms:count_total&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_fahrrad_stat/gdm_fahrrad_stat?request=getfeature&service=wfs&version=2.0.0&typename=ms:rad_heatmap&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/gdm_address/gdm_address?REQUEST=GetFeature&SRSNAME=EPSG:25832&SERVICE=WFS&VERSION=2.0.0&TYPENAMES=addresses&OUTPUTFORMAT=CSV",
    "https://geoportal.freiburg.de/wfs/gdm_address/gdm_address?request=getfeature&service=wfs&version=2.0.0&typename=ms:addresses_streets&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/fa_befall/fa_befall?request=getfeature&service=wfs&version=2.0.0&typename=ms:befall&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/aki_kita/aki_kita?request=getfeature&service=wfs&version=2.0.0&typename=ms:kita_fritz&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/aki_kita/aki_kita?request=getfeature&service=wfs&version=2.0.0&typename=ms:kita_waldwaegen&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/aki_kita/aki_kita?request=getfeature&service=wfs&version=2.0.0&typename=ms:okja&outputformat=csv&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:begegnungsst&outputformat=csv&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:beratung_aeltere&outputformat=csv&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:pflegeeinrichtungen&outputformat=csv&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:seniorenwohnanlagen&outputformat=csv&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:wohnstift&outputformat=csv&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:tagespflege&outputformat=csv&srsname=epsg:25832",
    # "https://geoportal.freiburg.de/wfs/afs_begegnungsstaetten/afs_begegnungsstaetten?request=getfeature&service=wfs&version=2.0.0&typename=ms:pflegewohngruppe&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak_test_alle?request=getfeature&service=wfs&version=2.0.0&typename=ms:evakuierungsradius&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak_test_alle?request=getfeature&service=wfs&version=2.0.0&typename=ms:geb_in_radius&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak_test_alle?request=getfeature&service=wfs&version=2.0.0&typename=ms:addr_in_radius&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak?request=getfeature&service=wfs&version=2.0.0&typename=ms:evakuierungsradius&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak?request=getfeature&service=wfs&version=2.0.0&typename=ms:geb_in_radius&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/afo_evak/afo_evak?request=getfeature&service=wfs&version=2.0.0&typename=ms:addr_in_radius&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_flaeche&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_01&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_02&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_03&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_04&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_05&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_06&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_07&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_08&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_09&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_10&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_11&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_12&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_13&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_14&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_15&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_16&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_umrisse&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abk_feuerwehr/abk_feuerwehr?request=getfeature&service=wfs&version=2.0.0&typename=ms:loeschbez_standorte&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abi_gsb/abi_gsb?request=getfeature&service=wfs&version=2.0.0&typename=ms:grundschulbezirke&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abi_gsb/abi_gsb?request=getfeature&service=wfs&version=2.0.0&typename=ms:grundschulstandorte&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:baubloecke&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:statistische_bezirke&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtbezirke&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtteile&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtbereiche&outputformat=csv&srsname=epsg:25832",
    "https://geoportal.freiburg.de/wfs/abi_gliederung/abi_gliederung?request=getfeature&service=wfs&version=2.0.0&typename=ms:stadtteile_out&outputformat=csv&srsname=epsg:25832"
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

    text = StringIO(r.content.decode('utf-8'))
    try:
        df = pd.read_csv(text)
    except pd.errors.ParserError:
        print(url, 'Parse Error CSV')
    df_new = pd.DataFrame()
    for col in df.columns:
        try:
            df[col] = df[col].apply(ast.literal_eval)
            s = df[col].explode()
            s = pd.concat([s, s.apply(pd.Series)], axis=1).drop(col, axis=1)
            s = s.reset_index()
            df_new = df_new.merge(s, how='left', left_on=df_new.index, right_on='index')
        except Exception as e:
            df_new[col] = df[col]

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
