create table if not exists public.memories_v2 (
    memory_id text primary key,
    user_id text not null,
    content text not null,
    memory_type text not null default 'fact',
    importance integer not null default 50,
    source text not null default 'chat',
    schema_version text not null default 'memory_v2',
    created_at timestamptz not null,
    last_seen_at timestamptz not null,
    hit_count integer not null default 1,
    metadata jsonb not null default '{}'::jsonb
);

create index if not exists idx_memories_v2_user_id
on public.memories_v2 (user_id);

create index if not exists idx_memories_v2_user_last_seen
on public.memories_v2 (user_id, last_seen_at desc);

create index if not exists idx_memories_v2_user_importance
on public.memories_v2 (user_id, importance desc);

create index if not exists idx_memories_v2_content_trgm
on public.memories_v2
using gin (content gin_trgm_ops);

alter table public.memories_v2
enable row level security;
