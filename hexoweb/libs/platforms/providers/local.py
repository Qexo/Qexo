from ..core import Provider
import os
import subprocess
import logging


class Local(Provider):
    name = "本地"

    def __init__(self, path, config, auto=False):
        super(Local, self).__init__(config)
        self.path = path
        self.auto = auto

    params = {"path": {"description": "博客路径", "placeholder": "博客源码的绝对路径"},
              "auto": {"description": "自动部署", "placeholder": "自动部署命令 留空不开启"}}

    def get_content(self, file):  # 获取文件内容UTF8
        with open(os.path.join(self.path, file), 'r', encoding='UTF-8') as f:
            logging.info("获取文件{}成功".format(os.path.join(self.path, file)))
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
        _path = os.path.join(self.path, path)
        contents = os.listdir(_path)
        for file in contents:
            filedir = os.path.join(_path, file)
            if not os.path.isdir(filedir):
                results.append({
                    "name": file,
                    "size": os.stat(filedir).st_size,
                    "path": os.path.join(path, file).replace("\\", "/"),
                    "type": "file"
                })
            else:
                results.append({
                    "name": file,
                    "path": os.path.join(path, file).replace("\\", "/"),
                    "type": "dir"
                })
        logging.info("获取路径{}成功".format(path))
        return {"path": path, "data": results}

    def save(self, file, content, commitchange="Update by Qexo", autobuild=True):
        path = os.path.join(self.path, file).replace("\\", "/")
        if not os.path.exists("/".join(path.split("/")[0:-1])):
            os.makedirs("/".join(path.split("/")[0:-1]))
        with open(path, "w", encoding="UTF-8") as f:
            f.write(content)
            logging.info("保存文件{}成功".format(file))
        if autobuild:
            return self.build()
        else:
            return autobuild

    def delete(self, path, commitchange="Delete by Qexo", autobuild=True):
        path = os.path.join(self.path, path)
        if os.path.isdir(path):
            os.removedirs(path)
            logging.info("删除目录{}成功".format(path))
        else:
            os.remove(path)
            logging.info("删除文件{}成功".format(path))
        if autobuild:
            return self.build()
        else:
            return autobuild

    def build(self):
        if not self.auto:
            return False
        logging.info("进行自动部署...")
        if os.name == 'nt':
            exec_cmd = "powershell \"cd {}; {}\"".format(self.path, self.auto)
        else:
            exec_cmd = "cd {} && {}".format(self.path, self.auto)
        logging.info(exec_cmd)
        p = subprocess.Popen(exec_cmd, shell=True)
        return p
