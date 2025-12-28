from typing import List,Dict, TypedDict


class Chunk(TypedDict):
    content: str
    chunk_index: int
    token_count: int
    page: int