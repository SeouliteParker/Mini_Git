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

    def test_error_messages(self):
        self.assertEqual(execute(self.git, "INIT"), "Invalid args")
        execute(self.git, "INIT Alice")
        self.assertEqual(execute(self.git, "SWITCH missing"), "Unknown branch: missing")
        self.assertEqual(execute(self.git, 'COMMIT "unfinished'), "Invalid args")


if __name__ == "__main__":
    unittest.main()
