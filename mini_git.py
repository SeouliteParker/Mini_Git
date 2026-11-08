"""Mini Git의 저장소·브랜치·커밋 관리 로직."""
from datetime import datetime

from commit import Commit


class MiniGit:
    def __init__(self):
        self.initialized = False
        self.author = ""
        self.current_branch = ""
        self.branches: dict[str, str | None] = {}
        self.commits: dict[str, Commit] = {}
        self.next_commit_id = 1

    def init(self, user_name: str) -> str:
        """빈 저장소를 초기화하고 main을 HEAD 브랜치로 설정한다."""
        if not user_name.strip():
            return "Invalid args"
        self.initialized = True
        self.author = user_name
        self.current_branch = "main"
        self.branches = {"main": None}
        self.commits = {}
        self.next_commit_id = 1
        return f"Initialized repository.\nCurrent branch: main\nCurrent user: {user_name}"

    def _require_init(self) -> str | None:
        return None if self.initialized else "Repository not initialized. Run INIT first."

    def branch(self, name: str) -> str:
        """현재 HEAD를 가리키는 새 브랜치를 만든다."""
        if error := self._require_init():
            return error
        if not name.strip() or any(char.isspace() for char in name):
            return "Invalid args"
        if name in self.branches:
            return f"Branch already exists: {name}"
        self.branches[name] = self.branches[self.current_branch]
        return f"Created branch: {name}"

    def switch(self, name: str) -> str:
        """브랜치를 이동하되 커밋 그래프는 변경하지 않는다."""
        if error := self._require_init():
            return error
        if name not in self.branches:
            return f"Unknown branch: {name}"
        self.current_branch = name
        return f"Switched to branch: {name}"

    def commit(self, message: str) -> str:
        """현재 브랜치 HEAD를 부모로 하는 새 커밋을 추가한다."""
        if error := self._require_init():
            return error
        if not message.strip():
            return "Invalid args"
        commit_hash = f"{self.next_commit_id:08x}"
        self.next_commit_id += 1
        parent = self.branches[self.current_branch]
        parents = [parent] if parent is not None else []
        new_commit = Commit(
            hash=commit_hash,
            message=message,
            author=self.author,
            timestamp=datetime.now().astimezone(),
            parents=parents,
        )
        self.commits[commit_hash] = new_commit
        self.branches[self.current_branch] = commit_hash
        return f"[{self.current_branch} {commit_hash}] {message}"

    def status(self) -> str:
        """학습을 위한 브랜치와 커밋 개수 요약."""
        if error := self._require_init():
            return error
        head = self.branches[self.current_branch] or "(no commits)"
        return f"Branch: {self.current_branch}\nHEAD: {head}\nCommits: {len(self.commits)}"
