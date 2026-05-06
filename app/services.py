import asyncio
import re
from bs4 import BeautifulSoup
from collections import Counter
from httpx import AsyncClient
from typing import Any


async def get_top_story_ids(client: AsyncClient) -> list[int]:
    """
    Get all top story ids from Hacker News.
    """

    response = await client.get('/topstories.json')
    response.raise_for_status()
    return response.json()
    

async def get_item(client: AsyncClient, item_id: int) -> dict[str, Any]:
    """
    Get a single HN item.
    """

    response = await client.get(f'/item/{item_id}.json')
    response.raise_for_status()
    return response.json()

async def get_items(client: AsyncClient, ids: list[int]) -> list[dict[str, Any]]:
    """
    Get multiple items at the same time
    """

    tasks = [get_item(client, item_id) for item_id in ids]
    return await asyncio.gather(*tasks)


async def get_top_stories(client: AsyncClient, limit: int=100) -> list[dict[str, Any]]:
    """
    Get the first 100 top stories
    """

    story_ids = await get_top_story_ids(client)
    top_story_ids = story_ids[:limit]
    return await get_items(client, top_story_ids)


def extract_top_level_comment_ids(stories: list[dict[str, Any]], limit: int=50) -> list[int]:
    """
    Get top-level comment ids from stories.
    """

    comment_ids = []
    for story in stories:
        for kid in story.get('kids', []):
            comment_ids.append(kid)
            if len(comment_ids) >= limit:
                return comment_ids
    return comment_ids


async def get_comments(client: AsyncClient, comment_ids: list[int]) -> list[dict[str, Any]]:
    """
    Get and filter valid comments.
    """
    comments = await get_items(client, comment_ids)
    filtered_comments = []
    for comment in comments:
        if not comment:
            continue
        if comment.get('type') != 'comment':
            continue
        if comment.get('deleted', False):
            continue
        if comment.get('dead', False):
            continue
        filtered_comments.append(comment)
    return filtered_comments


def serialize_comment(
    comment: dict[str, Any],
) -> dict[str, Any]:
    """
    Clean HN payload into a clean API response.
    """

    return {
        'id': comment.get('id'),
        'author': comment.get('by'),
        'text': clean_html(comment.get('text')),
        'time': comment.get('time'),
        'parent': comment.get('parent'),
    }


async def get_first_50_comments(client: AsyncClient) -> list[dict[str, Any]]:
    """
    Get the first 50 top-level comments from the first 100 top stories.
    """

    stories = await get_top_stories(client=client, limit=100)
    comment_ids = extract_top_level_comment_ids(stories, limit=50)
    comments = await get_comments(client=client, comment_ids=comment_ids)
    first_50_comments = comments[:50]

    return [serialize_comment(comment) for comment in first_50_comments]


def clean_html(text: str | None) -> str:
    """
    Clean comments from html tags and decode html entitites.
    """
    if not text:
        return ''
    return BeautifulSoup(text, 'html.parser').get_text(separator=' ')



class CommentAnalysisService:

    def tokenize(self, text: str) -> list[str]:
        text = text.lower()
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"[^a-z0-9\s']", "", text)
        return [word for word in text.split() if word]

    def get_top_words(self, comments: list[dict[str, Any]], top_n: int = 10 ) -> list[dict[str, Any]]:
        counter = Counter()
        for comment in comments: 
            text = clean_html(comment.get('text')) or ''
            tokens = self.tokenize(text)
            counter.update(tokens)
        return [ {'word': word, 'count': count} for word, count in counter.most_common(top_n) ]
    

async def get_top_words_from_top_comments(client: AsyncClient) -> list[dict[str, Any]]:
    """
    Get top 10 most used words from the first 100 top-level comments of the top 30 stories.
    """

    stories = await get_top_stories(client=client, limit=30)
    comment_ids = extract_top_level_comment_ids(stories, limit=150)
    comments = await get_comments(client=client, comment_ids=comment_ids)
    comments = comments[:100]
    analyzer = CommentAnalysisService()
    return analyzer.get_top_words(comments, top_n=10)


async def get_all_comments_for_story(client: AsyncClient, story: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Fetch all comments) for a single story using BFS.
    """

    all_comments = []
    queue = story.get('kids', [])[:]

    while queue:
        # process in batches
        batch_ids = queue[:100]
        queue = queue[100:]

        items = await get_items(client, batch_ids)

        for item in items:
            if not item:
                continue

            # collect valid comments
            if (
                item.get('type') == 'comment'
                and not item.get('deleted', False)
                and not item.get('dead', False)
            ):
                all_comments.append(item)

            kids = item.get('kids', [])
            if kids:
                queue.extend(kids)

    return all_comments



async def get_all_comments_from_top_stories(client: AsyncClient, limit: int = 10,) -> list[dict[str, Any]]:
    """
    Get ALL comments from top N stories.
    """

    stories = await get_top_stories(client=client, limit=limit)
    tasks = [get_all_comments_for_story(client, story) for story in stories if story]
    results = await asyncio.gather(*tasks)

    all_comments = [
        comment
        for story_comments in results
        for comment in story_comments
    ]
    return all_comments



async def get_top_words_from_all_comments(client: AsyncClient) -> list[dict[str, Any]]:
    """
    Get most used words from ALL comments of top 10 stories.
    """

    comments = await get_all_comments_from_top_stories(client, limit=10)
    analyzer = CommentAnalysisService()
    return analyzer.get_top_words(comments, top_n=10)


