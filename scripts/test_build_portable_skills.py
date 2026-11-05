import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import build_portable_skills as build


class FrontmatterTest(unittest.TestCase):
    def test_moves_non_spec_fields_into_metadata(self):
        converted = build.convert_frontmatter(
            "name: demo\n"
            "description: Use when: testing\n"
            "disable-model-invocation: true\n"
            "allowed-tools:\n  - Read\n  - Glob\n"
            "metadata:\n  version: 1.0\n"
        )
        self.assertEqual(
            converted,
            'name: "demo"\n'
            'description: "Use when: testing"\n'
            "metadata:\n"
            '  disable-model-invocation: "true"\n'
            '  allowed-tools: "Read Glob"\n'
            '  version: "1.0"',
        )

    def test_keeps_block_descriptions(self):
        converted = build.convert_frontmatter(
            "name: demo\ndescription: >\n  First line\n  second line\n"
        )
        self.assertIn("description: >\n  First line\n  second line", converted)


class BuildTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.plugin = self.root / "plugins" / "demo"
        self.write(self.plugin / "shared" / "loop.md", "See [writing](writing.md).\n")
        self.write(self.plugin / "shared" / "writing.md", "Plain.\n")
        self.write(
            self.plugin / "skills" / "one" / "SKILL.md",
            "---\nname: one\ndescription: First\ndisable-model-invocation: true\n---\n"
            "Use [loop](../../shared/loop.md), [two](../two/SKILL.md), AskUserQuestion.\n"
            "Example only: [users](../../data-model/users.md).\n",
        )
        self.write(
            self.plugin / "skills" / "two" / "SKILL.md",
            "---\nname: two\ndescription: Second\n---\nBody.\n",
        )
        self.output = self.root / "skills"
        skills = {"one", "two"}
        self.output.mkdir()
        build.build_skill(self.plugin / "skills" / "one", self.output / "one", skills)

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def test_copies_shared_files_and_their_links(self):
        shared = self.output / "one" / "references" / "shared"
        self.assertEqual((shared / "loop.md").read_text(), "See [writing](writing.md).\n")
        self.assertEqual((shared / "writing.md").read_text(), "Plain.\n")

    def test_rewrites_only_links_that_resolve(self):
        body = (self.output / "one" / "SKILL.md").read_text()
        self.assertIn("[loop](references/shared/loop.md)", body)
        self.assertIn("[two](../two/SKILL.md)", body)
        self.assertIn("[users](../../data-model/users.md)", body)

    def test_adds_notes_and_tool_map(self):
        body = (self.output / "one" / "SKILL.md").read_text()
        self.assertIn(build.USER_ONLY_NOTE, body)
        self.assertIn(build.TOOL_NOTE, body)
        self.assertTrue((self.output / "one" / "references" / "tool-names.md").is_file())

    def test_check_reports_a_changed_file(self):
        copy = self.root / "copy"
        copy.mkdir()
        (copy / "a.md").write_text("old")
        other = self.root / "other"
        other.mkdir()
        (other / "a.md").write_text("new")
        self.assertEqual(build.differences(copy, other), [Path("a.md")])


if __name__ == "__main__":
    unittest.main()
