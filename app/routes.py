from fastapi import APIRouter, Depends
from httpx import AsyncClient

from .deps import get_client
from .services import get_first_50_comments, get_top_words_from_top_comments

router = APIRouter()


@router.get('/top-50-comments')
async def top_50_comments(client: AsyncClient = Depends(get_client)):
    return await get_first_50_comments(client)

@router.get('/top-10-words')
async def top_10_words(client: AsyncClient = Depends(get_client)):
    return await get_top_words_from_top_comments(client)