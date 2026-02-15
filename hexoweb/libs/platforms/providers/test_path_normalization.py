import unittest
from unittest.mock import MagicMock, patch

from hexoweb.libs.platforms.providers.gitEa import GitEa
from hexoweb.libs.platforms.providers.gitHub import Github
from hexoweb.libs.platforms.providers.gitLab import Gitlab


class ProviderPathNormalizationTests(unittest.TestCase):
    @patch("hexoweb.libs.platforms.providers.gitHub.github.Github")
    def test_github_path_adds_trailing_slash_for_subdir(self, github_cls):
        repo = MagicMock()
        github_cls.return_value.get_repo.return_value = repo
        provider = Github("token", "owner/repo", "main", "blog", "Hexo")

        provider.get_content("package.json")

        repo.get_contents.assert_called_once_with("blog/package.json", "main")

    @patch("hexoweb.libs.platforms.providers.gitLab.gitlab.Gitlab")
    def test_gitlab_path_normalizes_leading_and_trailing_slashes(self, gitlab_cls):
        project = MagicMock()
        gitlab_cls.return_value.projects.get.return_value = project

        provider = Gitlab("", "token", "1", "main", "/blog/", "Hexo")

        self.assertEqual(provider.path, "blog/")

    def test_gitea_root_path_keeps_empty_prefix(self):
        provider = GitEa("https://example.com", "token", "owner/repo", "main", "/", "Hexo")

        self.assertEqual(provider.path, "")


if __name__ == "__main__":
    unittest.main()
