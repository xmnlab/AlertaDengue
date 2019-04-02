# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-27 00:23
from __future__ import unicode_literals

from django.db import migrations

import sys


def create_dengue_global():
    if 'test' in sys.argv:
        sql = '''
            CREATE SCHEMA IF NOT EXISTS "Dengue_global";

            CREATE TABLE IF NOT EXISTS "Dengue_global"."Municipio"
            (
              geocodigo integer NOT NULL,
              nome character varying(128) NOT NULL,
              geojson text NOT NULL,
              populacao bigint NOT NULL,
              uf character varying(20) NOT NULL,
              CONSTRAINT "Municipio_pk" PRIMARY KEY (geocodigo)
            );

            CREATE TABLE IF NOT EXISTS "Dengue_global"."CID10"
            (
              nome character varying(512) NOT NULL,
              codigo character varying(5) NOT NULL,
              CONSTRAINT "CID10_pk" PRIMARY KEY (codigo)
            );
        '''
    else:
        sql = 'SELECT 1;'

    return migrations.RunSQL(sql, hints={'target_db': 'forecast'})


class Migration(migrations.Migration):
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[create_dengue_global()]
        )
    ]
