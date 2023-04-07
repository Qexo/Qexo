# https://vuepress.vuejs.org/
config = {
    "name": "Vuepress",
    "posts": {
        "path": [""],
        "depth": [-1],
        "type": [".md"],
        "save_path": "${filename}.md",
        "scaffold": "",
        "excludes": [".vuepress"]
    },
    "drafts": {   # No drafts in Vuepress
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
        "excludes": [".vuepress"]
    },
    "configs": {
        "path": [".vuepress"],
        "depth": [2],
        "type": [".yml", ".yaml", ".toml", ".js", ".json", ".styl", ".html", ".vue"]
    }
}
