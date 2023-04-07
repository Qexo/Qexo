# https://vitepress.dev/
config = {
    "name": "Vitepress",
    "posts": {
        "path": [""],
        "depth": [-1],
        "type": [".md"],
        "save_path": "${filename}.md",
        "scaffold": "",
        "excludes": [".vitepress"]
    },
    "drafts": {   # No drafts in Vitepress
        "path": [""],
        "depth": [],
        "type": [],
        "save_path": "",
        "scaffold": ""
    },
    "pages": {  # Same as posts
        "path": [""],
        "depth": [-1],
        "type": [".md"],
        "save_path": "${filename}.md",
        "scaffold": "",
        "excludes": [".vitepress"]
    },
    "configs": {
        "path": [".vitepress"],
        "depth": [2],
        "type": [".yml", ".yaml", ".toml", ".js", ".json", ".styl", ".html", ".vue"]
    }
}
