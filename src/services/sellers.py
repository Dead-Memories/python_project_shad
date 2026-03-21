from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.sellers import Seller
from src.schemas.sellers import IncomingSeller, PatchSeller, UpdateSeller

__all__ = ["SellerService"]


class SellerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_seller(self, seller: IncomingSeller) -> Seller:
        new_seller = Seller(
            first_name=seller.first_name,
            last_name=seller.last_name,
            e_mail=seller.e_mail,
            password=seller.password,
        )
        self.session.add(new_seller)
        await self.session.flush()
        return new_seller

    async def get_all_sellers(self) -> list[Seller]:
        query = select(Seller)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_single_seller(self, seller_id: int) -> Seller | None:
        query = (
            select(Seller)
            .options(selectinload(Seller.books))
            .where(Seller.id == seller_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_seller(
        self,
        seller_id: int,
        new_seller_data: UpdateSeller,
    ) -> Seller | None:
        updated_seller = await self.session.get(Seller, seller_id)
        if updated_seller is None:
            return None

        updated_seller.first_name = new_seller_data.first_name
        updated_seller.last_name = new_seller_data.last_name
        updated_seller.e_mail = new_seller_data.e_mail

        await self.session.flush()
        return updated_seller

    async def partial_update_seller(
        self,
        seller_id: int,
        patched_seller: PatchSeller,
    ) -> Seller | None:
        seller = await self.session.get(Seller, seller_id)
        if seller is None:
            return None

        if patched_seller.first_name is not None:
            seller.first_name = patched_seller.first_name

        if patched_seller.last_name is not None:
            seller.last_name = patched_seller.last_name

        if patched_seller.e_mail is not None:
            seller.e_mail = patched_seller.e_mail

        await self.session.flush()
        return seller

    async def delete_seller(self, seller_id: int) -> bool:
        seller = await self.session.get(Seller, seller_id)
        if seller is None:
            return False

        await self.session.delete(seller)
        return True