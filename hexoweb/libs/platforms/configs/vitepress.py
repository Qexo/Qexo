# https://vitepress.dev/
config = {
    "name": "Vitepress",
    "posts": {
        "path": ["blogs", "posts", "articles", "archives"],
        "depth": [-1, -1, -1, -1],
        "type": [".md"],
        "save_path": "${filename}.md",
        "scaffold": "",
        "excludes": [".vitepress"]
    },
    "drafts": {  # No drafts in Vitepress
        "path": [],
        "depth": [],
        "type": [],
        "save_path": None,
        "scaffold": ""
    },
    "pages": {
        "path": [""],
        "depth": [-1],
        "type": [".md"],
        "save_path": "${filename}.md",
        "scaffold": "",
        "excludes": [".vitepress", "blogs", "posts", "articles", "archives"]
    },
    "configs": {
        "path": [".github", ".vitepress", ""],
        "depth": [3, 2, 1],
        "type": [".yml", ".yaml", ".toml", ".js", ".ts", ".json", ".styl", ".html", ".vue"]
    }
}
