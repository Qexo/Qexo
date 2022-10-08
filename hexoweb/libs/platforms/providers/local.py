from ..core import Provider
import os


class Local(Provider):
    name = "本地"

    def __init__(self, path):
        self.path = path

    params = {'path': {"description": "Hexo 路径", "placeholder": "Hexo源码的绝对路径"}}

    def get_content(self, file):  # 获取文件内容UTF8
        with open(os.path.join(self.path, file), 'r', encoding='UTF-8') as f:
            print("获取文件{}成功".format(os.path.join(self.path, file)))
            return f.read()

    def get_path(self, path):  # 获取目录下的文件列表
        """
        :param path: 目录路径
        :return: {
            "data":[{"type":"dir/file", "name":"文件名", "path":"文件路径", "size":"文件大小(仅文件)"}, ...],
            "path":"当前路径"
            }
        """
        results = list()
        path = os.path.join(self.path, path)
        contents = os.listdir(path)
        for file in contents:
            filedir = os.path.join(path, file)
            if not os.path.isdir(filedir):
                results.append({
                    "name": file,
                    "size": os.stat(filedir).st_size,
                    "path": filedir.replace("\\", "/"),
                    "type": "file"
                })
            else:
                results.append({
                    "name": file,
                    "path": filedir.replace("\\", "/"),
                    "type": "dir"
                })
        print("获取路径{}成功".format(path))
        return {"path": path, "data": results}

    def save(self, file, content, commitchange="Update by Qexo"):
        path = os.path.join(self.path, file).replace("\\", "/")
        if not os.path.exists("/".join(path.split("/")[0:-1])):
            os.makedirs("/".join(path.split("/")[0:-1]))
        with open(path, "w", encoding="UTF-8") as f:
            f.write(content)
            print("保存文件{}成功".format(file))
        return True

    def delete(self, path, commitchange="Delete by Qexo"):
        path = os.path.join(self.path, path)
        if os.path.isdir(path):
            os.removedirs(path)
            print("删除目录{}成功".format(path))
        else:
            os.remove(path)
            print("删除文件{}成功".format(path))
        return True
