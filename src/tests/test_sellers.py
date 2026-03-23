import pytest
from fastapi import status
from sqlalchemy import select

from src.models.books import Book
from src.models.sellers import Seller

API_V1_URL_PREFIX = "/api/v1/seller"


# Тест на ручку, создающую селлера 
@pytest.mark.asyncio()
async def test_create_seller(async_client):
    data = {
        "first_name": "Olya",
        "last_name": "Khramova",
        "e_mail": "olya@example.com",
        "password": "123456",
    }

    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()
    resp_seller_id = result_data.pop("id", None)

    assert resp_seller_id is not None, "Seller id not returned from endpoint"
    assert "password" not in result_data
    assert result_data == {
        "first_name": "Olya",
        "last_name": "Khramova",
        "e_mail": "olya@example.com",
    }

# Тест на ручку, возвращающую список всех селлеров
# дополнительно проверяем, что пароль не возвращается в ответе
@pytest.mark.asyncio()
async def test_get_sellers(db_session, async_client):
    seller_1 = Seller(
        first_name="Olya",
        last_name="Khramova",
        e_mail="olya@example.com",
        password="123456",
    )
    seller_2 = Seller(
        first_name="Anna",
        last_name="Petrova",
        e_mail="anna@example.com",
        password="qwerty",
    )

    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK

    sellers = response.json()["sellers"]
    sellers = sorted(sellers, key=lambda item: item["id"])

    assert len(sellers) == 2
    assert sellers == [
        {
            "id": seller_1.id,
            "first_name": "Olya",
            "last_name": "Khramova",
            "e_mail": "olya@example.com",
        },
        {
            "id": seller_2.id,
            "first_name": "Anna",
            "last_name": "Petrova",
            "e_mail": "anna@example.com",
        },
    ]

    for seller in sellers:
        assert "password" not in seller

# Тест на ручку, возвращающую селлера по id 
@pytest.mark.asyncio()
async def test_get_single_seller(db_session, async_client, auth_seller):
    seller, headers = auth_seller

    book = Book(
        title="Clean Architecture",
        author="Robert Martin",
        year=2025,
        pages=300,
        seller_id=seller.id,
    )
    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(
        f"{API_V1_URL_PREFIX}/{seller.id}",
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": seller.id,
        "first_name": "Olya",
        "last_name": "Khramova",
        "e_mail": "olya@example.com",
        "books": [
            {
                "id": book.id,
                "title": "Clean Architecture",
                "author": "Robert Martin",
                "year": 2025,
                "pages": 300,
                "seller_id": seller.id,
            }
        ],
    }
    assert "password" not in response.json()

# Тест на ручку, возвращающую селлера по id, если id не существует
@pytest.mark.asyncio()
async def test_get_single_seller_with_wrong_id(async_client, auth_seller):
    _, headers = auth_seller

    response = await async_client.get(
        f"{API_V1_URL_PREFIX}/999999",
        headers=headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


# Тест на ручку обновления селлера
@pytest.mark.asyncio()
async def test_update_seller(db_session, async_client):
    seller = Seller(
        first_name="Olya",
        last_name="Khramova",
        e_mail="olya@example.com",
        password="123456",
    )
    db_session.add(seller)
    await db_session.flush()

    data = {
        "first_name": "Olga",
        "last_name": "Sidorova",
        "e_mail": "olga@example.com",
    }

    response = await async_client.put(
        f"{API_V1_URL_PREFIX}/{seller.id}",
        json=data,
    )

    assert response.status_code == status.HTTP_200_OK

    updated_seller = await db_session.get(Seller, seller.id)
    assert updated_seller is not None
    assert updated_seller.first_name == "Olga"
    assert updated_seller.last_name == "Sidorova"
    assert updated_seller.e_mail == "olga@example.com"
    assert updated_seller.password == "123456"

# Тест на ручку удаления селлера
@pytest.mark.asyncio()
async def test_delete_seller(db_session, async_client):
    seller = Seller(
        first_name="Olya",
        last_name="Khramova",
        e_mail="olya@example.com",
        password="123456",
    )
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    deleted_seller = await db_session.get(Seller, seller.id)
    assert deleted_seller is None


# Проверка, что удаление селлера удаляет его книги
@pytest.mark.asyncio()
async def test_delete_seller_deletes_books(db_session, async_client):
    seller = Seller(
        first_name="Olya",
        last_name="Khramova",
        e_mail="olya@example.com",
        password="123456",
    )
    db_session.add(seller)
    await db_session.flush()

    book = Book(
        title="Clean Architecture",
        author="Robert Martin",
        year=2025,
        pages=300,
        seller_id=seller.id,
    )
    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    deleted_seller = await db_session.get(Seller, seller.id)
    assert deleted_seller is None

    all_books = await db_session.execute(select(Book))
    books = all_books.scalars().all()
    assert len(books) == 0
