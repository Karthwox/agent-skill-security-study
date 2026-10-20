-- Notes app schema

create table public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  display_name text,
  role text not null default 'user' check (role in ('user', 'admin')),
  plan text not null default 'free',
  created_at timestamptz not null default now()
);

create table public.notes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  title text not null,
  body text not null default '',
  created_at timestamptz not null default now()
);

create function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = ''
as $$
begin
  insert into public.profiles (id, display_name)
  values (new.id, new.raw_user_meta_data ->> 'display_name');
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

alter table public.profiles enable row level security;
alter table public.notes enable row level security;

create policy "profiles: read own" on public.profiles for select to authenticated
  using ((select auth.uid()) = id);

create policy "notes: read own" on public.notes for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "notes: insert own" on public.notes for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy "notes: update own" on public.notes for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy "notes: delete own" on public.notes for delete to authenticated
  using ((select auth.uid()) = user_id);
