--
-- PostgreSQL database cluster dump
--

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE "Dengue";
ALTER ROLE "Dengue" WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB NOLOGIN NOREPLICATION NOBYPASSRLS VALID UNTIL 'infinity';
CREATE ROLE administrador;
ALTER ROLE administrador WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN NOREPLICATION NOBYPASSRLS PASSWORD NULL;
CREATE ROLE dengue;
ALTER ROLE dengue WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB LOGIN NOREPLICATION NOBYPASSRLS VALID UNTIL 'infinity';
-- CREATE ROLE dengueadmin;
-- ALTER ROLE dengueadmin WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN NOREPLICATION NOBYPASSRLS PASSWORD NULL VALID UNTIL 'infinity';
ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION NOBYPASSRLS;

--
-- Role memberships
--
GRANT "Dengue" TO dengue GRANTED BY administrador;
GRANT "Dengue" TO dengueadmin GRANTED BY administrador;
--
-- PostgreSQL database cluster dump complete
--