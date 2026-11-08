"""Mini Git 핵심 기능 및 경계 조건 회귀 테스트."""
import unittest

from main import execute
from mini_git import MiniGit


class MiniGitTests(unittest.TestCase):
    def setUp(self):
        self.git = MiniGit()

    def test_requires_init(self):
        self.assertIn("not initialized", execute(self.git, 'COMMIT "Hi"'))

    def test_init_and_commit(self):
        self.assertIn("Initialized", execute(self.git, 'init "Alice Smith"'))
        self.assertIn("00000001", execute(self.git, 'commit "Initial commit"'))
        commit = self.git.commits["00000001"]
        self.assertEqual(commit.author, "Alice Smith")
        self.assertEqual(commit.parents, [])
        self.assertEqual(self.git.branches["main"], "00000001")

    def test_branch_independence(self):
        execute(self.git, "INIT Alice")
        execute(self.git, 'COMMIT "First"')
        execute(self.git, "BRANCH feature")
        execute(self.git, "SWITCH feature")
        execute(self.git, 'COMMIT "Feature change"')
        self.assertEqual(self.git.commits["00000002"].parents, ["00000001"])
        self.assertEqual(self.git.branches["feature"], "00000002")
        self.assertEqual(self.git.branches["main"], "00000001")

    def test_log_parent_before_children(self):
        execute(self.git, "INIT Alice")
        execute(self.git, 'COMMIT "Initial commit"')
        execute(self.git, "BRANCH feature")
        execute(self.git, "SWITCH feature")
        execute(self.git, 'COMMIT "Add login feature"')
        execute(self.git, "SWITCH main")
        execute(self.git, 'COMMIT "Add payment feature"')
        output = execute(self.git, "LOG")
        self.assertLess(output.index("commit 00000001"), output.index("commit 00000002"))
        self.assertLess(output.index("commit 00000001"), output.index("commit 00000003"))
        self.assertIn("Parents: 00000001", output)

    def test_log_empty_and_invalid_args(self):
        self.assertIn("not initialized", execute(self.git, "LOG"))
        execute(self.git, "INIT Alice")
        self.assertEqual(execute(self.git, "LOG"), "No commits.")
        self.assertEqual(execute(self.git, "LOG extra"), "Invalid args")

    def test_path_between_branches(self):
        execute(self.git, "INIT Alice")
        execute(self.git, 'COMMIT "Initial"')
        execute(self.git, "BRANCH feature")
        execute(self.git, "SWITCH feature")
        execute(self.git, 'COMMIT "Login"')
        execute(self.git, "SWITCH main")
        execute(self.git, 'COMMIT "Payment"')
        execute(self.git, 'COMMIT "Extra"')
        self.assertEqual(
            execute(self.git, "PATH 00000002 00000004"),
            "Path: 00000002 -> 00000001 -> 00000003 -> 00000004"
        )
        self.assertEqual(execute(self.git, "PATH 00000002 00000002"),
                         "Path: 00000002")
        self.assertEqual(execute(self.git, "PATH 00000002 ffffffff"),
                         "Unknown commit: ffffffff")
        self.assertEqual(execute(self.git, "PATH 00000002"), "Invalid args")

    def test_path_lexicographic_tie(self):
        """동일 최단 거리의 경로는 첫 분기에서 작은 해시를 택한다."""
        from commit import Commit
        from datetime import datetime
        execute(self.git, "INIT Alice")
        t = datetime.now()
        self.git.commits = {
            key: Commit(key, key, "Alice", t, parents)
            for key, parents in (
                ("1", []), ("2", ["1"]), ("3", ["1"]),
                ("4", ["2", "3"]), ("5", ["2", "3"])
            )
        }
        self.assertEqual(execute(self.git, "PATH 4 5"), "Path: 4 -> 2 -> 5")

    def test_ancestors_linear_and_branch(self):
        execute(self.git, "INIT Alice")
        execute(self.git, 'COMMIT "Initial"')
        execute(self.git, 'COMMIT "Second"')
        execute(self.git, 'COMMIT "Third"')
        self.assertEqual(execute(self.git, "ANCESTORS 00000003"),
                         "Ancestors: 00000001, 00000002")
        self.assertEqual(execute(self.git, "ANCESTORS 00000001"),
                         "No ancestors")
        self.assertEqual(execute(self.git, "ANCESTORS ffffffff"),
                         "Unknown commit: ffffffff")
        self.assertEqual(execute(self.git, "ANCESTORS"), "Invalid args")

    def test_ancestors_multiple_parents_deduplicated(self):
        from commit import Commit
        from datetime import datetime
        execute(self.git, "INIT Alice")
        t = datetime.now()
        self.git.commits = {
            key: Commit(key, key, "Alice", t, parents)
            for key, parents in (
                ("1", []), ("2", ["1"]), ("3", ["1"]),
                ("4", ["2", "3"])
            )
        }
        self.assertEqual(execute(self.git, "ANCESTORS 4"),
                         "Ancestors: 1, 2, 3")

    def test_search_keyword_case_and_duplicate(self):
        execute(self.git, "INIT Alice")
        execute(self.git, 'COMMIT "Login login feature"')
        execute(self.git, 'COMMIT "Fix payment"')
        execute(self.git, 'COMMIT "Improve LOGIN"')
        result = execute(self.git, "SEARCH login")
        self.assertIn("Found 2 commits:", result)
        self.assertIn("00000001", result)
        self.assertIn("00000003", result)
        self.assertNotIn("00000002", result)
        self.assertEqual(execute(self.git, "SEARCH LOGIN"), result)

    def test_search_author_and_missing(self):
        execute(self.git, 'INIT "Alice Smith"')
        execute(self.git, 'COMMIT "Initial commit"')
        execute(self.git, 'COMMIT "Add feature"')
        result = execute(self.git, 'SEARCH --author="Alice Smith"')
        self.assertIn("Found 2 commits:", result)
        self.assertIn("00000001", result)
        self.assertIn("00000002", result)
        self.assertEqual(execute(self.git, "SEARCH --author=Bob"), "No commits found.")
        self.assertEqual(execute(self.git, "SEARCH unknown"), "No commits found.")
        self.assertEqual(execute(self.git, "SEARCH --author="), "Invalid args")
        self.assertEqual(execute(self.git, "SEARCH"), "Invalid args")

    def test_search_index_reset_on_init(self):
        execute(self.git, "INIT Alice")
        execute(self.git, 'COMMIT "Old login"')
        execute(self.git, "INIT Bob")
        self.assertEqual(execute(self.git, "SEARCH login"), "No commits found.")
        execute(self.git, 'COMMIT "New login"')
        self.assertIn("00000001", execute(self.git, "SEARCH login"))
        self.assertEqual(execute(self.git, "SEARCH --author=Alice"), "No commits found.")

    def test_log_sort_by_date_and_author(self):
        from datetime import datetime, timedelta, timezone
        execute(self.git, "INIT Alice")
        execute(self.git, 'COMMIT "First"')
        execute(self.git, 'COMMIT "Second"')
        execute(self.git, 'COMMIT "Third"')
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.git.commits["00000001"].timestamp = base + timedelta(days=2)
        self.git.commits["00000002"].timestamp = base
        self.git.commits["00000003"].timestamp = base + timedelta(days=1)
        self.git.commits["00000001"].author = "Zoe"
        self.git.commits["00000002"].author = "alice"
        self.git.commits["00000003"].author = "Bob"
        for command, expected in (
            ("LOG", ["00000001", "00000002", "00000003"]),
            ("LOG --sort-by=date", ["00000002", "00000003", "00000001"]),
            ("LOG --sort-by=author", ["00000002", "00000003", "00000001"]),
        ):
            output = execute(self.git, command)
            found = [line.split(" (")[0].removeprefix("commit ")
                     for line in output.splitlines() if line.startswith("commit ")]
            self.assertEqual(found, expected)
        self.assertEqual(execute(self.git, "LOG --sort-by=message"), "Invalid args")
        self.assertEqual(execute(self.git, "LOG --sort-by=date extra"), "Invalid args")

    def test_merge_sort_stable_and_empty(self):
        from sorting import merge_sort
        self.assertEqual(merge_sort([], key=lambda x: (x,)), [])
        self.assertEqual(merge_sort([3, 1, 2, 1], key=lambda x: (x,)),
                         [1, 1, 2, 3])
        items = [("a", 2), ("b", 1), ("c", 2)]
        self.assertEqual(merge_sort(items, key=lambda x: (x[1],)),
                         [("b", 1), ("a", 2), ("c", 2)])

    def test_path_disconnected_components(self):
        """서로 다른 루트에서 시작하는 커밋은 경로가 없다."""
        from commit import Commit
        from datetime import datetime, timezone
        execute(self.git, "INIT Alice")
        t = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.git.commits = {
            "a": Commit("a", "Root A", "Alice", t, []),
            "b": Commit("b", "Child B", "Alice", t, ["a"]),
            "c": Commit("c", "Root C", "Alice", t, []),
        }
        self.assertEqual(execute(self.git, "PATH b c"), "No path")
        self.assertEqual(execute(self.git, "PATH a b"), "Path: a -> b")

    def test_branch_created_before_first_commit(self):
        """빈 브랜치에서 시작한 커밋은 독립 루트가 된다."""
        execute(self.git, "INIT Alice")
        self.assertEqual(execute(self.git, "BRANCH empty"), "Created branch: empty")
        execute(self.git, "SWITCH empty")
        self.assertIn("HEAD: (no commits)", execute(self.git, "STATUS"))
        execute(self.git, 'COMMIT "Feature root"')
        self.assertEqual(self.git.commits["00000001"].parents, [])
        execute(self.git, "SWITCH main")
        self.assertIn("HEAD: (no commits)", execute(self.git, "STATUS"))
        execute(self.git, 'COMMIT "Main root"')
        self.assertEqual(self.git.commits["00000002"].parents, [])
        self.assertEqual(execute(self.git, "PATH 00000001 00000002"), "No path")

    def test_log_sort_ties_by_hash(self):
        """같은 날짜·작성자라면 hash 오름차순으로 정렬한다."""
        from datetime import datetime, timezone
        execute(self.git, "INIT Alice")
        for message in ("One", "Two", "Three"):
            execute(self.git, f'COMMIT "{message}"')
        same_time = datetime(2026, 2, 3, tzinfo=timezone.utc)
        for commit in self.git.commits.values():
            commit.timestamp = same_time
        expected = ["00000001", "00000002", "00000003"]
        for command in ("LOG --sort-by=date", "LOG --sort-by=author"):
            output = execute(self.git, command)
            hashes = [line.split(" (")[0].removeprefix("commit ")
                      for line in output.splitlines() if line.startswith("commit ")]
            self.assertEqual(hashes, expected)

    def test_log_sort_empty_repository(self):
        execute(self.git, "INIT Alice")
        self.assertEqual(execute(self.git, "LOG --sort-by=date"), "No commits.")
        self.assertEqual(execute(self.git, "LOG --sort-by=author"), "No commits.")

    def test_log_parent_first_on_multiple_branches(self):
        """해시 번호와 무관하게 모든 부모를 자식보다 먼저 출력한다."""
        execute(self.git, "INIT Alice")
        execute(self.git, 'COMMIT "Root"')
        execute(self.git, "BRANCH feature")
        execute(self.git, "SWITCH feature")
        execute(self.git, 'COMMIT "Feature first"')
        execute(self.git, 'COMMIT "Feature second"')
        execute(self.git, "SWITCH main")
        execute(self.git, 'COMMIT "Main first"')
        output = execute(self.git, "LOG")
        hashes = [line.split(" (")[0].removeprefix("commit ")
                  for line in output.splitlines() if line.startswith("commit ")]
        positions = {commit_hash: index for index, commit_hash in enumerate(hashes)}
        self.assertEqual(len(hashes), 4)
        for commit_hash, commit in self.git.commits.items():
            for parent_hash in commit.parents:
                self.assertLess(positions[parent_hash], positions[commit_hash])

    def test_invalid_commands_keep_state(self):
        """잘못된 명령은 브랜치 HEAD나 커밋 수를 바꾸지 않는다."""
        execute(self.git, "INIT Alice")
        execute(self.git, 'COMMIT "Root"')
        before = execute(self.git, "STATUS")
        for command in (
            "SWITHCH feature",
            "SWITCH missing",
            "BRANCH main",
            "BRANCH bad name",
            "COMMIT",
            'COMMIT ""',
            "PATH 00000001",
            "ANCESTORS",
            "SEARCH --author=",
            "LOG --sort-by=invalid",
        ):
            self.assertTrue(execute(self.git, command))
        self.assertEqual(execute(self.git, "STATUS"), before)

    def test_commands_are_case_insensitive(self):
        execute(self.git, "init Alice")
        execute(self.git, 'commit "Initial Login"')
        self.assertIn("00000001", execute(self.git, "log"))
        self.assertIn("00000001", execute(self.git, "search LOGIN"))
        self.assertIn("00000001", execute(self.git, "log --sort-by=date"))

    def test_error_messages(self):
        self.assertEqual(execute(self.git, "INIT"), "Invalid args")
        execute(self.git, "INIT Alice")
        self.assertEqual(execute(self.git, "SWITCH missing"), "Unknown branch: missing")
        self.assertEqual(execute(self.git, 'COMMIT "unfinished'), "Invalid args")


if __name__ == "__main__":
    unittest.main()
