"""Mini Git의 저장소·브랜치·커밋 관리 로직."""
from datetime import datetime

from commit import Commit
from graph import parent_first, shortest_path, ancestors
from inverted_index import InvertedIndex


class MiniGit:
    def __init__(self):
        self.initialized = False
        self.author = ""
        self.current_branch = ""
        self.branches: dict[str, str | None] = {}
        self.commits: dict[str, Commit] = {}
        self.next_commit_id = 1
        self.index = InvertedIndex()

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
        self.index = InvertedIndex()
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
        self.index.add(commit_hash, message, self.author)
        self.branches[self.current_branch] = commit_hash
        return f"[{self.current_branch} {commit_hash}] {message}"

    def status(self) -> str:
        """학습을 위한 브랜치와 커밋 개수 요약."""
        if error := self._require_init():
            return error
        head = self.branches[self.current_branch] or "(no commits)"
        return f"Branch: {self.current_branch}\nHEAD: {head}\nCommits: {len(self.commits)}"

    def log(self) -> str:
        """부모 커밋을 자식 커밋보다 먼저 출력한다."""
        if error := self._require_init():
            return error
        if not self.commits:
            return "No commits."
        rows = []
        for commit in parent_first(self.commits):
            date = commit.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            parents = ", ".join(commit.parents) if commit.parents else "(root)"
            rows.append(
                f"commit {commit.hash} ({commit.author}, {date})\n"
                f"Parents: {parents}\n{commit.message}"
            )
        return "\n\n".join(rows)


    def path(self, first: str, second: str) -> str:
        """두 커밋 간 최단 경로를 출력한다."""
        if error := self._require_init():
            return error
        for commit_hash in (first, second):
            if commit_hash not in self.commits:
                return f"Unknown commit: {commit_hash}"
        result = shortest_path(self.commits, first, second)
        if result is None:
            return "No path"
        return "Path: " + " -> ".join(result)

    def ancestors(self, commit_hash: str) -> str:
        """지정한 커밋의 조상 목록을 출력한다."""
        if error := self._require_init():
            return error
        if commit_hash not in self.commits:
            return f"Unknown commit: {commit_hash}"
        result = ancestors(self.commits, commit_hash)
        return "Ancestors: " + ", ".join(result) if result else "No ancestors"

    def search(self, query: str, by_author: bool = False) -> str:
        """역색인에서 키워드 또는 작성자의 커밋 목록을 조회한다."""
        if error := self._require_init():
            return error
        if not query.strip():
            return "Invalid args"
        hashes = self.index.author(query) if by_author else self.index.keyword(query)
        if not hashes:
            return "No commits found."
        entries = [f"- {commit_hash}: {self.commits[commit_hash].message}"
                   for commit_hash in hashes]
        label = "commit" if len(hashes) == 1 else "commits"
        return f"Found {len(hashes)} {label}:\n" + "\n".join(entries)
