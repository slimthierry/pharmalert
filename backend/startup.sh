#!/bin/bash
set -e

echo "Running database migrations..."
python -c "
import asyncio
from app.config.database import engine
from app.models import Base

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('Tables created')

asyncio.run(create_tables())
"

echo "Seeding admin user..."
python -c "
import asyncio, bcrypt
from app.config.database import AsyncSessionLocal
from app.models.user_models import User, UserRole
from sqlalchemy import select, delete

async def seed():
    async with AsyncSessionLocal() as session:
        # Reset admin if exists
        await session.execute(delete(User).where(User.email == 'admin@pharmalert.com'))
        hashed = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
        admin = User(
            email='admin@pharmalert.com',
            name='Admin',
            hashed_password=hashed,
            role=UserRole.ADMIN
        )
        session.add(admin)
        await session.commit()
        print('Admin user ready: admin@pharmalert.com / admin123')

asyncio.run(seed())
"

echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 9600
