DROP TABLE IF EXISTS "Municipio"."Clima_Satelite";

CREATE TABLE IF NOT EXISTS "Municipio".satellite_climate
(
  id bigserial NOT NULL PRIMARY KEY,
  images_date DATE NOT NULL,
  geocode INTEGER NOT NULL,
  ndvi double precision NULL,
  temperature_max double precision NULL,
  temperature_min double precision NULL,
  precipitation double precision NULL,
  relative_humidity double precision NULL,
  specific_humidity double precision NULL,
  CONSTRAINT sattelite_climate_geocode_fkey FOREIGN KEY (geocode)
      REFERENCES "Dengue_global"."Municipio" (geocodigo) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  UNIQUE (images_date, geocode)
)