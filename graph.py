"""커밋 그래프 탐색: 부모 우선 DFS."""
from commit import Commit


def parent_first(commits: dict[str, Commit]) -> list[Commit]:
    """부모가 자식보다 먼저 나오는 위상 정렬 순서를 반환한다."""
    visited: set[str] = set()
    visiting: set[str] = set()
    result: list[Commit] = []

    def visit(commit_hash: str) -> None:
        if commit_hash in visited:
            return
        if commit_hash in visiting:
            raise ValueError("Commit graph contains a cycle")
        visiting.add(commit_hash)
        commit = commits[commit_hash]
        for parent_hash in commit.parents:
            if parent_hash not in commits:
                raise ValueError(f"Unknown parent: {parent_hash}")
            visit(parent_hash)
        visiting.remove(commit_hash)
        visited.add(commit_hash)
        result.append(commit)

    for commit_hash in commits:
        visit(commit_hash)
    return result
