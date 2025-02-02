import asyncpg
from config import DATABASE

async def create_db_pool():
    return await asyncpg.create_pool(DATABASE)

async def get_categories(pool):
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT id, name FROM categories")

async def get_cars_by_category(pool, category_id):
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT id, name, description FROM cars WHERE category_id = $1", category_id
        )

async def get_car_images(pool, car_id):
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT image FROM car_images WHERE car_id = $1", car_id)