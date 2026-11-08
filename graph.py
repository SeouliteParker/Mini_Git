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



def shortest_path(commits: dict[str, Commit], start: str, end: str) -> list[str] | None:
    """부모-자식 간선을 무방향으로 보아 최단 경로를 찾는다.

    동일 길이 경로가 여러 개라면 hash 경로 문자열의 사전순 최소를 택한다.
    목적지로부터 BFS 거리 계산 후, 시작점에서 거리가 줄어드는
    가장 작은 이웃을 차례로 선택한다.
    """
    from collections import deque

    adjacency: dict[str, set[str]] = {key: set() for key in commits}
    for commit in commits.values():
        for parent in commit.parents:
            if parent not in commits:
                continue
            adjacency[commit.hash].add(parent)
            adjacency[parent].add(commit.hash)

    distances = {end: 0}
    queue = deque([end])
    while queue:
        current = queue.popleft()
        for neighbor in adjacency[current]:
            if neighbor not in distances:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)

    if start not in distances:
        return None
    path = [start]
    current = start
    while current != end:
        options = [neighbor for neighbor in adjacency[current]
                   if distances.get(neighbor) == distances[current] - 1]
        current = min(options)
        path.append(current)
    return path


def ancestors(commits: dict[str, Commit], commit_hash: str) -> list[str]:
    """부모 방향으로 DFS를 수행하여 모든 조상을 중복 없이 찾는다.

    출발 커밋 자신은 결과에 포함하지 않으며 조상은 hash 오름차순으로 출력한다.
    """
    visited: set[str] = set()
    stack = list(commits[commit_hash].parents)
    while stack:
        parent = stack.pop()
        if parent in visited:
            continue
        visited.add(parent)
        if parent in commits:
            stack.extend(commits[parent].parents)
    # 정렬은 표준 정렬 API 없이 삽입 정렬로 처리한다.
    ordered: list[str] = []
    for item in visited:
        pos = len(ordered)
        ordered.append(item)
        while pos > 0 and ordered[pos - 1] > item:
            ordered[pos] = ordered[pos - 1]
            pos -= 1
        ordered[pos] = item
    return ordered
