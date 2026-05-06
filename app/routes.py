from fastapi import APIRouter, Depends
from httpx import AsyncClient

from .deps import get_client
from .services import get_first_50_comments

router = APIRouter()


@router.get('/top-50-comments')
async def top_50_comments(client: AsyncClient = Depends(get_client)):
    return await get_first_50_comments(client)