import asyncio

from werkzeug.security import generate_password_hash

from models import User
from models.models import AdminMessage, RepairRequest, RequestStatus, ServiceRecord
from settings import Base, api_config, async_engine, async_session


async def create_bd():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def insert_data():
    async with async_session() as session:
        u1 = User(
            username="admin",
            email="admin@ex.com",
            is_admin=True,
            password=generate_password_hash("admin"),
        )
        u2 = User(
            username="user",
            email="user@ex.com",
            password=generate_password_hash("user"),
        )

        u3 = User(
            username="egor",
            email="egor@ex.com",
            password=generate_password_hash("egor"),
        )

        session.add_all([u1, u2, u3])
        await session.flush()
        await session.refresh(u1)
        await session.refresh(u2)
        await session.refresh(u3)

        rec1 = RepairRequest(
            description="Зламався екран",
            photo_url=None,
            status=RequestStatus.NEW,
            user_id=u3.id,
        )
        rec2 = RepairRequest(
            description="Не працює кнопка",
            photo_url=None,
            status=RequestStatus.NEW,
            user_id=u2.id,
            admin_id=u1.id,
        )

        rec3 = RepairRequest(
            description="Не працює кнопка",
            photo_url=None,
            status=RequestStatus.IN_PROGRESS,
            user_id=u2.id,
            admin_id=u1.id,
        )

        session.add_all([rec1, rec2, rec3])
        await session.flush()
        await session.refresh(rec3)

        sr1 = ServiceRecord(
            pay="50$",
            parts_used="кнопка, расходні матеріали",
            warranty_info="2 years",
            request_id=rec3.id,
        )

        mess_3 = AdminMessage(message="необхідне уточнення про поломку",
                              request_id = rec3.id,
                              admin_id = u1.id)
        session.add_all([sr1, mess_3])
        await session.commit()


async def main():
    await create_bd()
    print(f"database {api_config.DATABASE_NAME} created")

    await insert_data()
    print(f"data added to {api_config.DATABASE_NAME}")

    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
