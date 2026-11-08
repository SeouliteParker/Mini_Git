"""Mini Git 1단계 회귀 테스트."""
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

    def test_error_messages(self):
        self.assertEqual(execute(self.git, "INIT"), "Invalid args")
        execute(self.git, "INIT Alice")
        self.assertEqual(execute(self.git, "SWITCH missing"), "Unknown branch: missing")
        self.assertEqual(execute(self.git, 'COMMIT "unfinished'), "Invalid args")


if __name__ == "__main__":
    unittest.main()
