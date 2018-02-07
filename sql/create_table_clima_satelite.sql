DROP TABLE IF EXISTS "Municipio"."Clima_Satelite";

CREATE TABLE IF NOT EXISTS "Municipio".clima_satelite
(
  id bigserial NOT NULL,
  images_date date NOT NULL,
  geocode integer NOT NULL,
  ndvi double precision NOT NULL,
  temperature_max double precision NOT NULL,
  temperature_min double precision NOT NULL,
  precipitation double precision NOT NULL,
  relative_humidity double precision NOT NULL,
  specific_humidity double precision NOT NULL,
  CONSTRAINT clima_satelite_pkey PRIMARY KEY (id),
  CONSTRAINT clima_satelite_geocodigo_fkey FOREIGN KEY (geocode)
      REFERENCES "Dengue_global"."Municipio" (geocodigo) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  UNIQUE (images_date, geocode)
)