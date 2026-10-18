import json

from django.test import TestCase, Client

from hexoweb.models import CustomModel
from hexoweb.functions import save_setting


class CustomFieldSandboxTests(TestCase):
    """/pub/get_custom/ 的 RestrictedPython 沙箱执行测试"""

    def setUp(self):
        self.client = Client()
        self.token = "test-token-123"
        # save_setting 会对 WEBHOOK_APIKEY 做 SHA-256 后存储，请求时传原文即可通过校验
        save_setting("WEBHOOK_APIKEY", self.token)

    def _create_field(self, name, content):
        return CustomModel.objects.create(name=name, content=content)

    def _call(self, key, extra=None):
        params = {"token": self.token, "key": key}
        params.update(extra or {})
        return json.loads(self.client.get("/pub/get_custom/", params).content)

    def test_print_output_is_returned(self):
        """回归：受限代码的 print 结果应作为 data 返回，而不是回显源码"""
        self._create_field("greet", "print('hello')")
        data = self._call("greet")
        self.assertTrue(data["status"])
        self.assertEqual(data["data"], "hello\n")

    def test_multiple_statements_are_executed(self):
        """多语句脚本应完整执行"""
        self._create_field("multi", "a = 1\nb = 2\nprint(a + b)")
        data = self._call("multi")
        self.assertEqual(data["data"], "3\n")

    def test_expression_is_evaluated(self):
        """纯表达式应回退为求值结果"""
        self._create_field("expr", "1 + 2")
        data = self._call("expr")
        self.assertEqual(data["data"], "3\n")

    def test_request_params_are_injected(self):
        """请求参数应作为变量注入执行环境"""
        self._create_field("param", "print('标题: ' + title)")
        data = self._call("param", {"title": "我的文章"})
        self.assertEqual(data["data"], "标题: 我的文章\n")

    def test_json_builtin_is_available(self):
        """注入的 json 模块在受限环境中可用，不会被 safe_globals 覆盖掉"""
        self._create_field("js", "print(json.dumps({'a': 1}))")
        data = self._call("js")
        self.assertEqual(data["data"], '{"a": 1}\n')

    def test_for_loop_requires_getiter_guard(self):
        """for 循环依赖 _getiter_ guard，缺失时会静默失败"""
        self._create_field("loop", "for i in range(3):\n    print(i)")
        data = self._call("loop")
        self.assertEqual(data["data"], "0\n1\n2\n")

    def test_function_definition_and_call(self):
        """受限代码可定义并调用函数"""
        self._create_field("func", "def f(n):\n    return n * 2\nprint(f(21))")
        data = self._call("func")
        self.assertEqual(data["data"], "42\n")

    def test_syntax_error_falls_back_to_source(self):
        """语法错误时保持既有行为：回显源码"""
        self._create_field("bad", "1 +")
        data = self._call("bad")
        self.assertEqual(data["data"], "1 +\n")

    def test_runtime_error_falls_back_to_source(self):
        """运行期错误时保持既有行为：回显源码"""
        self._create_field("err", "1 / 0")
        data = self._call("err")
        self.assertEqual(data["data"], "1 / 0\n")

    def test_sandbox_still_blocks_import(self):
        """安全回归：受限环境仍然禁止 import"""
        self._create_field("imp", "import os\nprint(os.getcwd())")
        data = self._call("imp")
        self.assertEqual(data["data"], "import os\nprint(os.getcwd())\n")

    def test_sandbox_still_blocks_dunder_attribute(self):
        """安全回归：受限环境仍然禁止访问下划线属性"""
        self._create_field("dunder", "print(''.__class__)")
        data = self._call("dunder")
        # 编译期即被拦截并回显源码；若沙箱失效则会输出 <class 'str'>
        self.assertNotIn("<class", data["data"])

    def test_guards_cannot_be_overridden_by_request_params(self):
        """安全回归：请求参数不得覆盖沙箱 guard"""
        self._create_field("greet", "print('hello')")
        data = self._call("greet", {"_print_": "overridden"})
        self.assertEqual(data["data"], "hello\n")

    def test_missing_token_is_rejected(self):
        """缺少 token 的请求应被拒绝"""
        self._create_field("greet", "print('hello')")
        data = json.loads(self.client.get("/pub/get_custom/", {"key": "greet"}).content)
        self.assertFalse(data["status"])
