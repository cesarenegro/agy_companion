import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.workspaces import WorkspaceRecord
from app.runtime.base import RuntimeMessageResult, RuntimeStreamChunk
from app.runtime.official_sdk import OfficialSdkError, validate_attachment_paths


class AttachmentValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        root = Path(self._temp_dir.name)
        self.workspace = WorkspaceRecord.sample(absolute_path=str(root))
        self.allowed_file = root / "allowed.txt"
        self.allowed_file.write_text("ok", encoding="utf-8")

    def tearDown(self) -> None:
        self._temp_dir.cleanup()

    def test_validate_attachment_paths_accepts_file_inside_workspace(self) -> None:
        resolved = validate_attachment_paths(self.workspace, [str(self.allowed_file)])
        self.assertEqual(resolved, [str(self.allowed_file.resolve())])

    def test_validate_attachment_paths_rejects_missing_file(self) -> None:
        missing = Path(self._temp_dir.name) / "missing.txt"
        with self.assertRaises(OfficialSdkError):
            validate_attachment_paths(self.workspace, [str(missing)])

    def test_validate_attachment_paths_rejects_file_outside_workspace(self) -> None:
        outside_dir = tempfile.TemporaryDirectory()
        try:
            outside_file = Path(outside_dir.name) / "outside.txt"
            outside_file.write_text("x", encoding="utf-8")
            with self.assertRaises(OfficialSdkError):
                validate_attachment_paths(self.workspace, [str(outside_file)])
        finally:
            outside_dir.cleanup()


class RuntimeMessageResultTests(unittest.TestCase):
    def test_stream_chunks_default_to_empty(self) -> None:
        result = RuntimeMessageResult(message_text="hello")
        self.assertEqual(result.stream_chunks, [])
        self.assertIsNone(result.approval_request)

    def test_stream_chunks_roundtrip(self) -> None:
        result = RuntimeMessageResult(
            message_text="hello",
            stream_chunks=[
                RuntimeStreamChunk(text="he", sequence=1),
                RuntimeStreamChunk(text="llo", sequence=2),
            ],
        )
        self.assertEqual("".join(chunk.text for chunk in result.stream_chunks), "hello")


if __name__ == "__main__":
    unittest.main()
