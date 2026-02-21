-- Enable UUID extension if not already enabled
create extension if not exists "uuid-ossp";

-- 1. Create Users Table
-- We create a custom users table in the public schema that references auth.users
create table public.users (
  id uuid references auth.users on delete cascade not null primary key,
  email text,
  full_name text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS for users
alter table public.users enable row level security;

-- Policies for users
create policy "Users can view their own profile."
  on public.users for select
  using ( auth.uid() = id );

create policy "Users can update their own profile."
  on public.users for update
  using ( auth.uid() = id );

-- 2. Create Ingredients Table
-- For users to store what they currently have in their pantry
create table public.ingredients (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.users(id) on delete cascade not null,
  name text not null,
  quantity numeric default 0,
  unit text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS for ingredients
alter table public.ingredients enable row level security;

-- Policies for ingredients
create policy "Users can manage their own ingredients."
  on public.ingredients for all
  using ( auth.uid() = user_id );

-- 3. Create Meal Plans Table
create table public.meal_plans (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.users(id) on delete cascade not null,
  title text not null,
  start_date date,
  end_date date,
  recipes jsonb, -- Storing the generated AI recipes for this plan as JSON
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS for meal plans
alter table public.meal_plans enable row level security;

-- Policies for meal plans
create policy "Users can manage their own meal plans."
  on public.meal_plans for all
  using ( auth.uid() = user_id );

-- 4. Trigger for new users
-- Automatically create a profile in public.users when a new user signs up
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.users (id, email, full_name)
  values (new.id, new.email, new.raw_user_meta_data->>'full_name');
  return new;
end;
$$ language plpgsql security definer;

-- Drop trigger if it exists. Useful if running this script multiple times.
drop trigger if exists on_auth_user_created on auth.users;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
