
config = {
    "name": "Nuxt",
    "posts": {
        "path": ["content/posts"],
        "depth": [-1],
        "type": [".md"],
        "save_path": "content/posts/${filename}.md",
        "scaffold": "scaffolds/post.md"
    },
        "drafts": {
        "path": ["content/drafts"],
        "depth": [-1],
        "type": [".md"],
        "save_path": "content/drafts/${filename}.md",
        "scaffold": "scaffolds/draft.md"
    },
    "pages": {
        "path": ["content"],
        "depth": [1],
        "type": ["index.md", "index.html", ".md", ".html"],
        "save_path": "content/${filename}.md",
        "scaffold": "scaffolds/page.md",
        "excludes": ["content/posts"]
    },
    "configs": {
        "path": [".github", "", "app"],
        "depth": [3, 1, 2],
        "type": [".ts", ".json", ".yml"]
    }
}
