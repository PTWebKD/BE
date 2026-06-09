import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models so Base.metadata is populated
from app.core.database import Base  # noqa
from app.modules.users.model import User, FitnessPassport, Follow  # noqa
from app.modules.auth.model import GuestOTP  # noqa
from app.modules.gym.model import Gym, GymMembership, WorkoutSession, ExerciseLog, GymAnnouncement  # noqa
from app.modules.food.model import FoodProduct, FoodOrder, FoodReview  # noqa
from app.modules.gear.model import GearItem, GearLifecycle, GearTransaction  # noqa
from app.modules.gamification.model import Challenge, UserChallenge, Badge  # noqa
from app.modules.fitcoin.model import FitcoinTransaction  # noqa
from app.modules.social.model import SocialPost  # noqa
from app.modules.notifications.model import Notification  # noqa
from app.core.config import settings  # noqa

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
