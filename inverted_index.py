"""Mini Git 역색인: 키워드·작성자에서 커밋 해시 목록으로 역방향 조회한다."""


class InvertedIndex:
    """공백 분리 키워드와 작성자별 커밋 해시 색인."""

    def __init__(self) -> None:
        self.by_keyword: dict[str, list[str]] = {}
        self.by_author: dict[str, list[str]] = {}

    def add(self, commit_hash: str, message: str, author: str) -> None:
        """커밋 생성 시 각 단어와 작성자를 색인한다.

        키워드는 공백 기준 split 후 소문자로 정규화한다.
        같은 메시지에 단어가 반복되어도 동일 커밋은 한 번만 색인한다.
        """
        for keyword in set(word.lower() for word in message.split()):
            self.by_keyword.setdefault(keyword, []).append(commit_hash)
        self.by_author.setdefault(author.lower(), []).append(commit_hash)

    def keyword(self, word: str) -> list[str]:
        """키워드가 일치하는 커밋 해시 목록을 조회한다."""
        return self.by_keyword.get(word.lower(), []).copy()

    def author(self, name: str) -> list[str]:
        """작성자가 일치하는 커밋 해시 목록을 조회한다."""
        return self.by_author.get(name.lower(), []).copy()
