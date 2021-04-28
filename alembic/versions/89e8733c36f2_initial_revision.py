"""Initial revision

Revision ID: 89e8733c36f2
Revises: 
Create Date: 2021-04-27 23:37:22.500465

"""
from mealie.core.config import settings
from mealie.core.security import get_password_hash
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89e8733c36f2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    categories_table = op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=False)
    op.create_index(op.f('ix_categories_slug'), 'categories', ['slug'], unique=True)
    custom_pages_table = op.create_table('custom_pages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    groups_table = op.create_table('groups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('webhook_enable', sa.Boolean(), nullable=False),
    sa.Column('webhook_time', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_groups_name'), 'groups', ['name'], unique=True)
    recipes_table = op.create_table('recipes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('image', sa.String(), nullable=True),
    sa.Column('totalTime', sa.String(), nullable=True),
    sa.Column('prepTime', sa.String(), nullable=True),
    sa.Column('performTime', sa.String(), nullable=True),
    sa.Column('cookTime', sa.String(), nullable=True),
    sa.Column('recipeYield', sa.String(), nullable=True),
    sa.Column('recipeCuisine', sa.String(), nullable=True),
    sa.Column('slug', sa.String(), nullable=True),
    sa.Column('dateAdded', sa.Date(), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('orgURL', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recipes_slug'), 'recipes', ['slug'], unique=True)
    sign_ups_table = op.create_table('sign_ups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sign_ups_name'), 'sign_ups', ['name'], unique=False)
    op.create_index(op.f('ix_sign_ups_token'), 'sign_ups', ['token'], unique=False)
    site_settings_table = op.create_table('site_settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('show_recent', sa.Boolean(), nullable=True),
    sa.Column('cards_per_section', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    site_theme_table = op.create_table('site_theme',
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    tags_table = op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=False)
    op.create_index(op.f('ix_tags_slug'), 'tags', ['slug'], unique=True)
    api_extras_table = op.create_table('api_extras',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('key_name', sa.String(), nullable=True),
    sa.Column('value', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['recipes.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key_name')
    )
    custom_pages2categories_table = op.create_table('custom_pages2categories',
    sa.Column('custom_page_id', sa.Integer(), nullable=True),
    sa.Column('category_slug', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['category_slug'], ['categories.slug'], ),
    sa.ForeignKeyConstraint(['custom_page_id'], ['custom_pages.id'], )
    )
    group2categories_table = op.create_table('group2categories',
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('category_slug', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['category_slug'], ['categories.slug'], ),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], )
    )
    mealplan_table = op.create_table('mealplan',
    sa.Column('uid', sa.Integer(), nullable=False),
    sa.Column('startDate', sa.Date(), nullable=True),
    sa.Column('endDate', sa.Date(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('uid'),
    sa.UniqueConstraint('uid')
    )
    notes_table = op.create_table('notes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('text', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['recipes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    recipe_instructions_table = op.create_table('recipe_instructions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('text', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['recipes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    recipe_nutrition_table = op.create_table('recipe_nutrition',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('calories', sa.String(), nullable=True),
    sa.Column('fatContent', sa.String(), nullable=True),
    sa.Column('fiberContent', sa.String(), nullable=True),
    sa.Column('proteinContent', sa.String(), nullable=True),
    sa.Column('sodiumContent', sa.String(), nullable=True),
    sa.Column('sugarContent', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['recipes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    recipes2categories_table = op.create_table('recipes2categories',
    sa.Column('recipe_id', sa.Integer(), nullable=True),
    sa.Column('category_slug', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['category_slug'], ['categories.slug'], ),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], )
    )
    recipes2tags_table = op.create_table('recipes2tags',
    sa.Column('recipe_id', sa.Integer(), nullable=True),
    sa.Column('tag_slug', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
    sa.ForeignKeyConstraint(['tag_slug'], ['tags.slug'], )
    )
    recipes_ingredients_table = op.create_table('recipes_ingredients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('ingredient', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['recipes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    site_settings2categories_table = op.create_table('site_settings2categories_table',
    sa.Column('sidebar_id', sa.Integer(), nullable=True),
    sa.Column('category_slug', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['category_slug'], ['categories.slug'], ),
    sa.ForeignKeyConstraint(['sidebar_id'], ['site_settings.id'], )
    )
    theme_colors_table = op.create_table('theme_colors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.String(), nullable=True),
    sa.Column('primary', sa.String(), nullable=True),
    sa.Column('accent', sa.String(), nullable=True),
    sa.Column('secondary', sa.String(), nullable=True),
    sa.Column('success', sa.String(), nullable=True),
    sa.Column('info', sa.String(), nullable=True),
    sa.Column('warning', sa.String(), nullable=True),
    sa.Column('error', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['site_theme.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    tools_table = op.create_table('tools',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('tool', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['recipes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    users_table = op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('admin', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_full_name'), 'users', ['full_name'], unique=False)
    webhook_urls_table = op.create_table('webhook_urls',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    meal_table = op.create_table('meal',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('slug', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('image', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['mealplan.uid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # seed data
    op.bulk_insert(site_settings_table, [
        {
            "id": 1,
            "language": "en",
            "firstDayOfWeek": 0,
            "showRecent": True,
        }
    ])
    op.bulk_insert(categories_table, [
        {"id": 1, "name": "thanksgiving", "slug": "thanksgiving"},
        {"id": 2, "name": "homechef", "slug": "homechef"},
        {"id": 3, "name": "potatoes", "slug": "potatoes"},
    ])
    op.bulk_insert(site_settings2categories_table, [
        {
            "sidebar_id": 1,
            "category_slug": "thanksgiving",
        },
        {
            "sidebar_id": 1,
            "category_slug": "homechef",
        },
        {
            "sidebar_id": 1,
            "category_slug": "potatoes",
        },
    ])
    op.bulk_insert(theme_colors_table, [
        {
            "parent_id": "default",
            "primary": "#E58325",
            "accent": "#00457A",
            "secondary": "#973542",
            "success": "#5AB1BB",
            "info": "#4990BA",
            "warning": "#FF4081",
            "error": "#EF5350",
        },
    ])
    op.bulk_insert(site_theme_table, [
        {
            "name": "default",
        },
    ])
    op.bulk_insert(groups_table, [
        {
            "id": 1,
            "name": settings.DEFAULT_GROUP,
            "webhook_enable": False,
            "webhook_time": "00:00",
        },
    ])
    op.bulk_insert(users_table, [
        {
            "id": 1,
            "full_name": "Change Me",
            "email": settings.DEFAULT_EMAIL,
            "password": get_password_hash(settings.DEFAULT_PASSWORD),
            "group_id": 1,
            "admin": True,
        },
    ])


def downgrade():
    op.drop_table('meal')
    op.drop_table('webhook_urls')
    op.drop_index(op.f('ix_users_full_name'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('tools')
    op.drop_table('theme_colors')
    op.drop_table('site_settings2categories')
    op.drop_table('recipes_ingredients')
    op.drop_table('recipes2tags')
    op.drop_table('recipes2categories')
    op.drop_table('recipe_nutrition')
    op.drop_table('recipe_instructions')
    op.drop_table('notes')
    op.drop_table('mealplan')
    op.drop_table('group2categories')
    op.drop_table('custom_pages2categories')
    op.drop_table('api_extras')
    op.drop_index(op.f('ix_tags_slug'), table_name='tags')
    op.drop_index(op.f('ix_tags_name'), table_name='tags')
    op.drop_table('tags')
    op.drop_table('site_theme')
    op.drop_table('site_settings')
    op.drop_index(op.f('ix_sign_ups_token'), table_name='sign_ups')
    op.drop_index(op.f('ix_sign_ups_name'), table_name='sign_ups')
    op.drop_table('sign_ups')
    op.drop_index(op.f('ix_recipes_slug'), table_name='recipes')
    op.drop_table('recipes')
    op.drop_index(op.f('ix_groups_name'), table_name='groups')
    op.drop_table('groups')
    op.drop_table('custom_pages')
    op.drop_index(op.f('ix_categories_slug'), table_name='categories')
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.drop_table('categories')
