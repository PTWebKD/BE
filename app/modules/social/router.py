from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.model import User
from .schema import PostCreate, PostOut
from . import service

router = APIRouter()


def ok(data):
    return {"success": True, "data": data}


@router.get("/feed")
async def feed(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    posts = await service.get_feed(db, user.user_id)
    return ok([PostOut.model_validate(p).model_dump() for p in posts])


@router.get("/posts")
async def all_posts(db: AsyncSession = Depends(get_db)):
    posts = await service.list_posts(db)
    return ok([PostOut.model_validate(p).model_dump() for p in posts])


@router.post("/posts")
async def create_post(
    data: PostCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await service.create_post(db, user, data)
    return ok(PostOut.model_validate(post).model_dump())


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_post(db, user, post_id)
    return ok({"deleted": post_id})


@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await service.like_post(db, post_id)
    return ok(PostOut.model_validate(post).model_dump())
