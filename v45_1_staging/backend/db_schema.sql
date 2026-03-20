-- PostgreSQL schema
CREATE TABLE tenants(id TEXT PRIMARY KEY);
CREATE TABLE users(id TEXT, tenant_id TEXT);
CREATE TABLE events(id TEXT, tenant_id TEXT, payload JSONB);
