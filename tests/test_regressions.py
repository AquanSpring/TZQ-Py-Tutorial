import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import _check_examples as checker

ROOT = pathlib.Path(__file__).resolve().parents[1]


class BuildTests(unittest.TestCase):
    def build(self, body):
        with tempfile.TemporaryDirectory() as work:
            root = pathlib.Path(work)
            shutil.copy2(ROOT / '_build_index.py', root / '_build_index.py')
            folder = root / 'python基础篇'
            folder.mkdir()
            (folder / '（00）测试.md').write_text('# 测试\n\n' + body, encoding='utf-8')
            result = subprocess.run(
                [sys.executable, '-X', 'utf8', '_build_index.py'], cwd=root,
                capture_output=True, text=True, encoding='utf-8', timeout=3)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return (root / 'index.html').read_text(encoding='utf-8')

    def test_pipe_without_table_separator_does_not_hang(self):
        for body in ['| plain text', '| heading |\nordinary text', '# ']:
            with self.subTest(body=body):
                page = self.build(body)
                self.assertIn('<p>' + ''.join(body.splitlines()).strip() + '</p>', page)

    def test_valid_table_still_renders(self):
        page = self.build('| name | value |\n| --- | --- |\n| a | 1 |')
        self.assertIn('<th>name</th><th>value</th>', page)
        self.assertIn('<td>a</td><td>1</td>', page)


class OutputTests(unittest.TestCase):
    def check(self, source, feed=''):
        problems = []
        with tempfile.TemporaryDirectory() as work:
            output = checker.run_script(work, 'example.py', source, problems, 'example.py', feed)
        self.assertIsNotNone(output, problems)
        checked = checker.check_source(source, output, problems, 'example.py')
        return checked, problems

    def test_swapped_comments_are_rejected(self):
        checked, problems = self.check('print(1) # 2\nprint(2) # 1\n')
        self.assertEqual(checked, 2)
        self.assertEqual(len(problems), 2)

    def test_another_print_cannot_supply_the_expected_value(self):
        checked, problems = self.check('print(1) # 2\nprint(2)\n')
        self.assertEqual(checked, 1)
        self.assertEqual(len(problems), 1)

    def test_function_calls_follow_runtime_order(self):
        checked, problems = self.check(
            'def first():\n    print(1) # 1\n'
            'def second():\n    print(2) # 2\nsecond()\nfirst()\n')
        self.assertEqual(checked, 2)
        self.assertEqual(problems, [])

    def test_repeated_calls_allow_multiple_outputs_from_the_same_line(self):
        checked, problems = self.check(
            'def show(value):\n    print(value) # 1\nshow(2)\nshow(1)\n')
        self.assertEqual(checked, 1)
        self.assertEqual(problems, [])

    def test_input_prompt_does_not_pollute_print_output(self):
        checked, problems = self.check('n = int(input("number: "))\nprint(n) # 3\n', '3\n')
        self.assertEqual(checked, 1)
        self.assertEqual(problems, [])

    def test_unexecuted_print_cannot_borrow_another_lines_output(self):
        checked, problems = self.check('if False:\n    print(2) # 2\nprint(2)\n')
        self.assertEqual(checked, 1)
        self.assertEqual(len(problems), 1)


if __name__ == '__main__':
    unittest.main()
