# https://hexo.io/
config = {
    "name": "Hexo",
    "posts": {
        "path": ["source/_posts"],
        "depth": [-1],
        "type": [".md"],
        "save_path": "source/_posts/${filename}.md",
        "scaffold": "scaffolds/post.md"
    },
    "drafts": {
        "path": ["source/_drafts"],
        "depth": [-1],
        "type": [".md"],
        "save_path": "source/_drafts/${filename}.md",
        "scaffold": "scaffolds/draft.md"
    },
    "pages": {
        "path": ["source"],
        "depth": [2],
        "type": ["index.md", "index.html", ".md", ".html"],
        "save_path": "source/${filename}.md",
        "scaffold": "scaffolds/page.md",
        "excludes": ["_posts", "_drafts"]
    },
    "configs": {
        "path": [".github", "", "themes", "source", "source/_data"],
        "depth": [3, 1, 2, 1, 1],
        "type": [".yml", ".yaml", ".toml", ".json"]
    }
}
