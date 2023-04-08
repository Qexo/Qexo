# https://vuepress.vuejs.org/
config = {
    "name": "Vuepress",
    "posts": {
        "path": ["blogs", "posts", "articles", "archives"],
        "depth": [-1, -1, -1, -1],
        "type": [".md"],
        "save_path": "${filename}.md",
        "scaffold": "",
        "excludes": [".vuepress"]
    },
    "drafts": {  # No drafts in Vuepress
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
        "excludes": [".vuepress", "blogs", "posts", "articles", "archives"]
    },
    "configs": {
        "path": [".github", ".vuepress", ""],
        "depth": [3, 2, 1],
        "type": [".yml", ".yaml", ".toml", ".js", ".ts", ".json", ".styl", ".html", ".vue"]
    }
}
