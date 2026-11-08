# Mini Git

Python 3.10+로 작성한 **학습용 CLI 기반 Mini Git** 프로젝트야. 실제 Git과 달리 **파일 내용, 네트워크, 영속 저장을 추적하지 않고 커밋 메타데이터**만 메모리에 저장해.

## 실행

```bash
python3 main.py
```

## 1~2단계 구현 진행

- `INIT <user_name>`: 저장소 초기화, main 브랜치 및 작성자 설정
- `COMMIT "<message>"`: 고유 커밋 해시 생성, 부모 커밋 연결, 브랜치 HEAD 갱신
- `BRANCH <branch_name>`: 현재 HEAD를 가리키는 새 브랜치 생성
- `SWITCH <branch_name>`: 현재 브랜치 전환
- `LOG`: 부모가 먼저 나오는 전체 커밋 기록(DFS 기반)
- `PATH <commit1> <commit2>`: 부모·자식 연결을 무방향으로 탐색하는 최단 경로(BFS), 동률 사전순 최소
- `STATUS`: 현재 브랜치, HEAD, 총 커밋 수 확인 (학습 보조 명령)
- 대소문자 구분 없는 명령, 따옴표로 감싼 공백 포함 인자, 기본 오류 처리

## 직접 실행해 보기

```text
mini-git> INIT "Alice"
mini-git> COMMIT "Initial commit"
mini-git> BRANCH feature
mini-git> SWITCH feature
mini-git> COMMIT "Add login feature"
mini-git> STATUS
mini-git> SWITCH main
mini-git> PATH 00000001 00000002
mini-git> STATUS
mini-git> exit
```

## 내부 구조

- `commit.py`: Commit(hash, message, author, timestamp, parents)
- `mini_git.py`: 저장소 상태, 브랜치 HEAD, 커밋 생성·관리
- `main.py`: shlex 파싱과 대화형 REPL
- `graph.py`: 부모 우선 DFS, BFS 최단 경로 탐색
- 커밋은 `dict[hash, Commit]`로 보관해 평균 O(1)에 찾는다.
- 각 커밋의 `parents`는 이전 커밋의 hash 목록이다. 새 커밋이 기존 커밋만 부모로 지정하므로 순환을 만들지 않는다.
- 해시는 세션 내 증가하는 카운터를 8자리 16진수로 변환한다. **실제 Git의 SHA 기반 콘텐츠 해시와 다른 학습용 식별자**이다.
- 메모리 저장 방식이므로 종료하면 기록이 사라진다.

## 아직 미구현 (후속 단계)

- `LOG --sort-by=date|author`
- `ANCESTORS`
- `SEARCH`, `SEARCH --author=<name>`
- 커밋 그래프 순회·BFS·위상 정렬·직접 구현 정렬·역색인
- 보너스: merge, diff, 정렬 성능 비교

## 테스트

```bash
python3 -m unittest discover -s tests -v
```
