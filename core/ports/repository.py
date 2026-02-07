from abc import ABC, abstractmethod
from typing import List
from core.entities.post import Post

class PostRepository(ABC):
    @abstractmethod
    def save(self, post: Post) -> None:
        pass

    @abstractmethod
    def get_all(self) -> List[Post]:
        pass

    @abstractmethod
    def delete(self, post_index: int) -> None:
        pass