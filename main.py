"""Mini Git CLI. 실행: python3 main.py"""
import shlex

from mini_git import MiniGit


def execute(git: MiniGit, line: str) -> str:
    """한 줄을 파싱한 후 대응하는 저장소 메서드를 호출한다."""
    try:
        args = shlex.split(line)
    except ValueError:
        return "Invalid args"
    if not args:
        return ""
    command = args[0].upper()
    if command in ("EXIT", "QUIT"):
        return "__EXIT__"
    if command == "INIT":
        return git.init(args[1]) if len(args) == 2 else "Invalid args"
    if command == "BRANCH":
        return git.branch(args[1]) if len(args) == 2 else "Invalid args"
    if command == "SWITCH":
        return git.switch(args[1]) if len(args) == 2 else "Invalid args"
    if command == "COMMIT":
        return git.commit(args[1]) if len(args) == 2 else "Invalid args"
    if command == "SEARCH":
        if len(args) != 2:
            return "Invalid args"
        if args[1].startswith("--author="):
            author = args[1][len("--author="):]
            return git.search(author, by_author=True) if author.strip() else "Invalid args"
        if args[1].startswith("--"):
            return "Invalid args"
        # 메시지를 공백 기준으로 분리해 색인하므로 단일 키워드만 허용한다.
        if len(args[1].split()) != 1:
            return "Invalid args"
        return git.search(args[1])
    if command == "ANCESTORS":
        return git.ancestors(args[1]) if len(args) == 2 else "Invalid args"
    if command == "PATH":
        return git.path(args[1], args[2]) if len(args) == 3 else "Invalid args"
    if command == "LOG":
        return git.log() if len(args) == 1 else "Invalid args"
    if command == "STATUS":
        return git.status() if len(args) == 1 else "Invalid args"
    return f"Unknown command: {args[0]}"


def main() -> None:
    git = MiniGit()
    print("Mini Git 실행! 종료: exit 또는 quit")
    while True:
        try:
            line = input("mini-git> ")
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        result = execute(git, line)
        if result == "__EXIT__":
            print("Bye!")
            break
        if result:
            print(result)


if __name__ == "__main__":
    main()
