from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update, func
from sqlalchemy.ext.asyncio import AsyncSession
import time
from database import get_async_session
from model.models import links
from .schemas import link
from pydantic import BaseModel
from cachetools import TTLCache, LRUCache
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from auth.users import auth_backend, current_active_user, fastapi_users
from auth.schemas import UserCreate, UserRead  # , UserUpdate
from auth.db import User, create_db_and_tables
from datetime import datetime
import uvicorn
from typing import Optional
from fastapi.responses import RedirectResponse
from config import base_url
from datetime import timedelta


router = APIRouter(prefix="/links", tags=["links"])

cache = LRUCache(maxsize=32)  # Максимум 32 записей в кэше
visit_counts = {}  # Отслеживаем количество посещений для каждого short_code


# Создание кастомных ссылок (уникальный alias) + Указание времени жизни ссылки:
@router.post("/shorten")
async def create_link(
    full_link: str,
    short_code: str,
    expires_at: Optional[datetime] = None,
    session: AsyncSession = Depends(get_async_session),
    user: Optional[User] = Depends(fastapi_users.current_user(optional=True)),
):
    """
    expires_at format: yyyy-mm-dd hh:mm
    """
    print(user)
    # Получим юзера
    if user:
        l = link(
            full_link=full_link,
            short_link=f"{base_url}/links/{short_code}",
            is_deleted=False,
            expiration_date=expires_at,
            login_user=user.email,
        )
        try:
            statement = insert(links).values(**l.dict(exclude_unset=True))
            await session.execute(statement)
            await session.commit()
            return {"status": "success", "new_link": l.short_link}
        except:
            return {"status": "short_link already exists"}
    else:
        l = link(
            full_link=full_link,
            short_link=f"{base_url}/links/{short_code}",
            is_deleted=False,
            expiration_date=expires_at,
        )
        try:
            statement = insert(links).values(**l.dict(exclude_unset=True))
            await session.execute(statement)
            await session.commit()
            return {"status": "success", "new_link": l.short_link}
        except:
            return {"status": "short_link already exists"}


@router.get("/{short_code}")
async def go_link(short_code: str, session: AsyncSession = Depends(get_async_session)):
    if short_code in cache:
        full_link, is_del, number_of_click, expiration_date = cache[short_code]
        print(f"Ссылка {short_code} получена из кэша")
        if is_del == False and datetime.now() < expiration_date:
            statement = (
                update(links)
                .where(links.c.short_link == f"{base_url}/links/{short_code}")
                .values(
                    {
                        links.c.number_of_click: number_of_click + 1,
                        links.c.date_use: datetime.now(),
                    }
                )
            )
            visit_counts[short_code] += 1
            await session.execute(statement)
            await session.commit()
            return RedirectResponse(url=full_link, status_code=302)
        else:
            return {"status": "link not available"}
    else:
        try:
            query = select(
                links.c.full_link,
                links.c.is_deleted,
                links.c.number_of_click,
                links.c.expiration_date,
            ).where(links.c.short_link == f"{base_url}/links/{short_code}")
            result = await session.execute(query)
            full_link, is_del, number_of_click, expiration_date = result.first()
            if (is_del == False) and (
                expiration_date is None or datetime.now() < expiration_date
            ):
                statement = (
                    update(links)
                    .where(links.c.short_link == f"{base_url}/links/{short_code}")
                    .values(
                        {
                            links.c.number_of_click: number_of_click + 1,
                            links.c.date_use: datetime.now(),
                        }
                    )
                )
                if short_code in visit_counts:
                    visit_counts[short_code] += 1
                else:
                    visit_counts[short_code] = 1

                if visit_counts[short_code] > 5:
                    cache[short_code] = (
                        full_link,
                        is_del,
                        number_of_click,
                        expiration_date,
                    )
                    print(f"Ссылка {short_code} добавлена в кэш")

                await session.execute(statement)
                await session.commit()
                return RedirectResponse(url=full_link, status_code=302)
            elif is_del == False and (
                expiration_date is None or datetime.now() > expiration_date
            ):
                statement = (
                    update(links)
                    .where(links.c.short_link == f"{base_url}/links/{short_code}")
                    .values(is_deleted=True)
                )
                await session.execute(statement)
                await session.commit()
                return {"status": "link already not available"}
            else:
                return {"status": "link not available"}
        except:
            return {"status": "link not found2"}


@router.delete("/{short_code}")
async def delete_link(
    short_code: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    is_deleted = select(links.c.is_deleted).where(
        links.c.short_link == f"{base_url}/links/{short_code}"
    )
    is_del = await session.execute(is_deleted)

    login = select(links.c.login_user).where(
        links.c.short_link == f"{base_url}/links/{short_code}"
    )
    login = await session.execute(is_deleted)
    login = login.first()

    if is_del.scalar() == False:
        if user.login == login:
            statement = (
                update(links)
                .where(links.c.short_link == f"{base_url}/links/{short_code}")
                .values(is_deleted=True)
            )
            await session.execute(statement)
            await session.commit()
            cache.pop(short_code, None)
            return {"status": "success", "is_deleted": "True"}
        else:
            return {"status": "this link was created by another user"}
    else:
        return {"status": "link not found or already is_deleted : True"}


@router.put("/{new_short_code}")
async def update_link(
    short_url_now: str,
    new_short_code: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    is_deleted = select(links.c.is_deleted).where(links.c.short_link == short_url_now)
    is_del = await session.execute(is_deleted)

    login = select(links.c.login_user).where(links.c.short_link == short_url_now)
    login = await session.execute(is_deleted)
    login = login.first()
    if is_del.scalar() == False:
        if user.login == login:
            statement = (
                update(links)
                .where(links.c.short_link == short_url_now)
                .values(short_link=f"{base_url}/links/{new_short_code}")
            )
            await session.execute(statement)
            await session.commit()
            return {
                "status": "success",
                "new_link": f"{base_url}/links/{new_short_code}",
            }
        else:
            return {"status": "this link was created by another user"}
    else:
        return {"status": "link not found or already is_deleted : True"}


# Получение статистики
@router.get("/{short_code}/stats")
async def statistic(
    short_code: str, session: AsyncSession = Depends(get_async_session)
):
    try:
        query = select(
            links.c.full_link,
            links.c.short_link,
            links.c.creation_date,
            links.c.number_of_click,
            links.c.date_use,
            links.c.is_deleted,
        ).where(links.c.short_link == f"{base_url}/links/{short_code}")
        result = await session.execute(query)
        full_link, short_link, creation_date, number_of_click, date_use, is_deleted = (
            result.first()
        )
        print(full_link)
        return {
            "full_link": full_link,
            "short_link": short_link,
            "creation_date": creation_date,
            "number_of_click": number_of_click,
            "date last use": date_use,
            "is_deleted": is_deleted,
        }
    except:
        print("Не нашли")
        return {"status": "link not found"}


# Поиск ссылки по оригинальному URL
@router.get("/search/full_url")
async def search_link(url: str, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(
            links.c.short_link, links.c.number_of_click, links.c.is_deleted
        ).where(links.c.full_link == url)
        result = await session.execute(query)
        rows = result.all()
        print(rows)
        statistics = []
        if rows:
            for row in rows:
                short_link, number_of_click, is_deleted = row
                statistics.append(
                    {
                        "short_link": short_link,
                        "number_of_click": number_of_click,
                        "is_deleted": is_deleted,
                    }
                )
            return statistics
        else:
            return {"status": "link not found"}
    except:
        return {"status": "link not nooo found"}


@router.post("/delete_time")
async def delete_link(
    day: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    if day > 0:
        statement = (
            update(links)  
            .where(
                links.c.date_use < func.now() - timedelta(days=day)
            )  
            .where(
                links.c.is_deleted == False
            )  
            .values(is_deleted=True)
        )

        result = await session.execute(statement)
        await session.commit()

        return {
            "status": "success",
            "deleted_count": result.rowcount,
        } 
    else:
        return {"status": "error, day < 0"}
