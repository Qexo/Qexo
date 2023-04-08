# https://valaxy.site/
config = {
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
        "type": [".yml", ".yaml", ".config.ts", ".toml", ".json"]
    }
}
