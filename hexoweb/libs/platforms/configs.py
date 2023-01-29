all_configs = ["Hexo", "Hugo"]

configs = {
    "Hexo": {
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
            "type": ["index.md", "index.html"],
            "save_path": "source/${filename}",
            "scaffold": "scaffolds/page.md"
        },
        "configs": {
            "path": ["", "themes", "source", "source/_data"],
            "depth": [1, 2, 1, 1],
            "type": [".yml", ".yaml"]
        }
    },

    "Hugo": {
        "name": "Hugo",
        "posts": {
            "path": ["content/post"],
            "depth": [2],
            "type": [".md"],
            "save_path": "content/post/${filename}.md",
            "scaffold": "scaffolds/post.md"
        },
        "drafts": {
            "path": [],
            "depth": [],
            "type": [".md"],
            "save_path": "content/post/${filename}.md",
            "scaffold": "scaffolds/draft.md"
        },
        "pages": {
            "path": ["content"],
            "depth": [2],
            "type": ["index.md", "index.html"],
            "save_path": "content/${filename}/index.md",
            "scaffold": "scaffolds/page.md"
        },
        "configs": {
            "path": ["", "themes"],
            "depth": [1, 2],
            "type": [".yml", ".yaml", ".toml"]
        }
    }
}
