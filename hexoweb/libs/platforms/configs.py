all_configs = ["Hexo", "Hugo", "Valaxy"]

configs = {
    # https://hexo.io/
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
            "type": ["index.md", "index.html", ".md", ".html"],
            "save_path": "source/${filename}",
            "scaffold": "scaffolds/page.md",
            "excludes": ["_posts", "_drafts"]
        },
        "configs": {
            "path": [".github", "", "themes", "source", "source/_data"],
            "depth": [3, 1, 2, 1, 1],
            "type": [".yml", ".yaml", ".toml"]
        }
    },
    # https://gohugo.io/
    "Hugo": {
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
            "type": [".yml", ".yaml", ".toml"]
        }
    },
    # https://valaxy.site/
    "Valaxy": {
        "name": "Valaxy",
        "posts": {
            "path": ["pages/posts"],
            "depth": [-1],
            "type": [".md"],
            "save_path": "pages/posts/${filename}.md",
            "scaffold": "scaffolds/post.md"
        },
        "drafts": {
            "path": ["pages/_drafts"],
            "depth": [-1],
            "type": [".md"],
            "save_path": "pages/_drafts/${filename}.md",
            "scaffold": "scaffolds/draft.md"
        },
        "pages": {
            "path": ["pages"],
            "depth": [2],
            "type": ["index.md", "index.html", ".md", ".html"],
            "save_path": "pages/${filename}",
            "scaffold": "scaffolds/page.md",
            "excludes": ["posts", "_drafts"]
        },
        "configs": {
            "path": [".github", ""],
            "depth": [3, 1],
            "type": [".yml", ".yaml", ".config.ts", ".toml"]
        }
    },

}
