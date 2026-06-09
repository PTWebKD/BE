from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.modules.users.model import User, Follow
from app.core.dependencies import err
from .model import SocialPost
from .schema import PostCreate


async def get_feed(db: AsyncSession, user_id: int) -> list:
    following_subq = select(Follow.following_id).where(Follow.follower_id == user_id)
    r = await db.execute(
        select(SocialPost)
        .where(or_(SocialPost.user_id == user_id, SocialPost.user_id.in_(following_subq)))
        .order_by(SocialPost.created_at.desc())
        .limit(50)
    )
    return r.scalars().all()


async def list_posts(db: AsyncSession) -> list:
    r = await db.execute(
        select(SocialPost).order_by(SocialPost.created_at.desc()).limit(100)
    )
    return r.scalars().all()


async def create_post(db: AsyncSession, user: User, data: PostCreate) -> SocialPost:
    post = SocialPost(
        user_id=user.user_id,
        type=data.type,
        content=data.content,
        media_urls=data.media_urls,
        linked_data=data.linked_data,
    )
    db.add(post)
    await db.flush()
    return post


async def delete_post(db: AsyncSession, user: User, post_id: int):
    r = await db.execute(select(SocialPost).where(SocialPost.post_id == post_id))
    post = r.scalar_one_or_none()
    if not post:
        err("NOT_FOUND", "Post not found", 404)
    if post.user_id != user.user_id:
        err("FORBIDDEN", "Not your post", 403)
    await db.delete(post)


async def like_post(db: AsyncSession, post_id: int) -> SocialPost:
    r = await db.execute(select(SocialPost).where(SocialPost.post_id == post_id))
    post = r.scalar_one_or_none()
    if not post:
        err("NOT_FOUND", "Post not found", 404)
    post.likes_count += 1
    await db.flush()
    return post
