# https://astro.build/
# 为 Astro 提供平台配置，仅识别 Markdown (.md) 和 HTML (.html) 文件
config = {
    "name": "Astro",
    "posts": {
        "path": ["src/content", "content", "src/pages", "src/pages/blog"],
        "depth": [-1, -1, -1, -1],
        "type": [".md", ".html"],
        "save_path": "src/content/${filename}.md",
        "scaffold": "scaffolds/post.md"
    },
    "drafts": {
        "path": ["src/drafts", "drafts"],
        "depth": [-1, -1],
        "type": [".md", ".html"],
        "save_path": "src/drafts/${filename}.md",
        "scaffold": "scaffolds/draft.md"
    },
    "pages": {
        "path": ["src/pages"],
        "depth": [-1],
        "type": [".md", ".html"],
        "save_path": "src/pages/${filename}.md",
        "scaffold": "scaffolds/page.md",
        "excludes": ["public", "components"]
    },
    "configs": {
        "path": ["", ".github", "src", "public"],
        "depth": [1, 3, 2, 1],
        "type": [".mjs", ".js", ".ts", ".json", ".toml", ".yaml", ".yml"]
    }
}

# 导出声明放在 config 之后，避免静态分析器警告
