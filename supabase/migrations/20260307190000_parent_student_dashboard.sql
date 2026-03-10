-- Migration: parent dashboard + student access enhancements
-- Safe to run multiple times (idempotent)

-- Needed for gen_random_uuid()
create extension if not exists pgcrypto;

-- 1) Students table enhancements
alter table if exists estudiantes
add column if not exists pin_hash text;

alter table if exists estudiantes
add column if not exists activo boolean not null default true;

alter table if exists estudiantes
add column if not exists desactivado_el timestamptz;

create index if not exists idx_estudiantes_padre_activo
on estudiantes (padre_id, activo);

-- 2) Energy consumption analytics table
create table if not exists consumo_energia (
  id uuid primary key default gen_random_uuid(),
  email_padre text not null,
  estudiante_id uuid references estudiantes(id),
  cantidad integer not null check (cantidad > 0),
  materia text,
  metadata jsonb not null default '{}'::jsonb,
  creado_el timestamptz not null default now()
);

create index if not exists idx_consumo_energia_padre_fecha
on consumo_energia (email_padre, creado_el);

create index if not exists idx_consumo_energia_estudiante_fecha
on consumo_energia (estudiante_id, creado_el);

-- 3) Optional hardening (RLS) for direct anon/authenticated clients.
-- Service-role operations from backend continue to work.
alter table if exists consumo_energia enable row level security;
