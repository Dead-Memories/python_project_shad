from pydantic import BaseModel

__all__ = [
    "IncomingSeller",
    "UpdateSeller",
    "PatchSeller",
    "ReturnedSeller",
    "ReturnedSellerWithBooks",
    "ReturnedAllSellers",
]


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: str


class UpdateSeller(BaseSeller):
    pass


class PatchSeller(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    e_mail: str | None = None


class IncomingSeller(BaseSeller):
    password: str


class ReturnedSeller(BaseSeller):
    id: int


class SellerBook(BaseModel):
    id: int
    title: str
    author: str
    year: int
    pages: int
    seller_id: int | None = None


class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[SellerBook] = []


class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]