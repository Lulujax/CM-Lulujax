import json
import os
from typing import List
from datetime import datetime
from core.ports.repository import PostRepository
from core.entities.post import Post

class JsonPostRepository(PostRepository):
    def __init__(self, file_path: str = "data/posts.json"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)

    def save(self, post: Post) -> None:
        posts = self._read_file()
        post_dict = {
            "image_path": post.image_path,
            "caption": post.caption,
            "schedule_time": post.schedule_time.isoformat()
        }
        posts.append(post_dict)
        self._write_file(posts)

    def get_all(self) -> List[Post]:
        data = self._read_file()
        post_objects = []
        for item in data:
            try:
                post = Post(
                    image_path=item["image_path"],
                    caption=item["caption"],
                    schedule_time=datetime.fromisoformat(item["schedule_time"])
                )
                post_objects.append(post)
            except Exception as e:
                print(f"Error cargando post: {e}")
        return post_objects

    def delete(self, post_index: int) -> None:
        posts = self._read_file()
        if 0 <= post_index < len(posts):
            posts.pop(post_index)
            self._write_file(posts)
        else:
            raise IndexError("Índice no válido.")

    def _read_file(self) -> list:
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_file(self, data: list) -> None:
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)