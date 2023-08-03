# https://gohugo.io/
config = {
    "name": "Hugo",
    "posts": {
        "path": ["content/posts"],
        "depth": [-1],
        "type": [".md"],
        "save_path": "content/posts/${filename}.md",
        "scaffold": "archetypes/post.md"
    },
    "drafts": {
        "path": ["content/_drafts"],
        "depth": [-1],
        "type": [".md"],
        "save_path": "content/_drafts/${filename}.md",
        "scaffold": "archetypes/draft.md"
    },
    "pages": {
        "path": ["content"],
        "depth": [3],
        "type": ["_index.md", "index.html", "index.md", ".md", ".html"],
        "save_path": "content/${filename}/index.md",
        "scaffold": "archetypes/page.md",
        "excludes": ["post", "_drafts"]
    },
    "configs": {
        "path": [".github", "", "themes", "config"],
        "depth": [3, 1, 2, 2],
        "type": [".yml", ".yaml", ".toml", ".json"]
    }
}
