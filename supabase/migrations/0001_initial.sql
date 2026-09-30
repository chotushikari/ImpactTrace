create extension if not exists vector;

create table if not exists projects (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  objective text,
  default_lat double precision,
  default_lng double precision,
  created_at timestamptz not null default now()
);

create table if not exists sites (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  name text not null,
  address text,
  lat double precision,
  lng double precision,
  geocode_source text
);

create table if not exists assets (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  site_id uuid references sites(id) on delete set null,
  cloudinary_asset_id text not null unique,
  cloudinary_public_id text not null,
  cloudinary_version bigint,
  resource_type text not null check (resource_type in ('image','video','raw')),
  format text,
  secure_url text not null,
  source_filename text,
  source_sha256 text,
  captured_at timestamptz,
  captured_at_source text,
  uploaded_at timestamptz not null default now(),
  lat double precision,
  lng double precision,
  location_source text,
  duration_seconds numeric,
  status text not null default 'queued' check (status in ('queued','processing','ready','failed')),
  created_at timestamptz not null default now()
);

create table if not exists observations (
  id uuid primary key default gen_random_uuid(),
  asset_id uuid not null references assets(id) on delete cascade,
  type text not null,
  text text,
  structured_json jsonb not null default '{}'::jsonb,
  model_provider text not null,
  model_name text not null,
  model_version text,
  confidence numeric check (confidence between 0 and 1),
  created_at timestamptz not null default now()
);

create table if not exists embeddings (
  id uuid primary key default gen_random_uuid(),
  asset_id uuid not null references assets(id) on delete cascade,
  modality text not null,
  model_name text not null,
  dimensions int not null,
  embedding vector(768),
  created_at timestamptz not null default now()
);

create table if not exists asset_relations (
  id uuid primary key default gen_random_uuid(),
  before_asset_id uuid not null references assets(id) on delete cascade,
  after_asset_id uuid not null references assets(id) on delete cascade,
  relation_type text not null,
  alignment_score numeric check (alignment_score between 0 and 1),
  created_at timestamptz not null default now()
);

create table if not exists change_observations (
  id uuid primary key default gen_random_uuid(),
  relation_id uuid not null references asset_relations(id) on delete cascade,
  description text not null,
  change_type text not null,
  confidence numeric not null check (confidence between 0 and 1),
  method text not null,
  model_provider text,
  model_name text,
  created_at timestamptz not null default now()
);

create table if not exists claims (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  text text not null,
  claim_type text not null check (claim_type in ('verified_fact','ai_observation','inference')),
  verification_status text not null default 'unverified',
  confidence numeric check (confidence between 0 and 1),
  created_at timestamptz not null default now()
);

create table if not exists evidence_links (
  id uuid primary key default gen_random_uuid(),
  claim_id uuid not null references claims(id) on delete cascade,
  asset_id uuid references assets(id) on delete cascade,
  observation_id uuid references observations(id) on delete cascade,
  relation_id uuid references asset_relations(id) on delete cascade,
  role text not null,
  created_at timestamptz not null default now(),
  check (asset_id is not null or observation_id is not null or relation_id is not null)
);

create table if not exists reports (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  title text not null,
  format text not null,
  storage_url text,
  source_manifest jsonb not null default '{}'::jsonb,
  generated_at timestamptz not null default now()
);

create index if not exists assets_project_idx on assets(project_id);
create index if not exists assets_site_idx on assets(site_id);
create index if not exists observations_asset_idx on observations(asset_id);
create index if not exists claims_project_idx on claims(project_id);
