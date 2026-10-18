"""
test_agent.py
Comprehensive unit tests for the AI Agent:
- Normal cases (direct response, tool decision, validation, successful save, approval)
- Failure cases (validation errors, path traversal, user rejection, max 5 calls limit, graceful error recovery)
"""

import os
import shutil
import tempfile
import unittest

from agent import AIAgent, AgentState
from tools import (
    ToolValidationError,
    save_note,
    validate_save_note_inputs,
    validate_save_note_output,
)


class TestToolValidation(unittest.TestCase):
    """Tests input and output validation for the save_note tool."""

    def test_valid_inputs(self):
        """Normal case: Valid inputs return normalized dictionary."""
        result = validate_save_note_inputs(
            title="Meeting Notes",
            content="Discussed Q4 AI goals and deliverables.",
            category="work",
        )
        self.assertEqual(result["title"], "Meeting Notes")
        self.assertEqual(result["content"], "Discussed Q4 AI goals and deliverables.")
        self.assertEqual(result["category"], "work")

    def test_empty_title_fails(self):
        """Failure case: Empty title should raise ToolValidationError."""
        with self.assertRaises(ToolValidationError):
            validate_save_note_inputs(title="   ", content="Valid content")

    def test_empty_content_fails(self):
        """Failure case: Empty content should raise ToolValidationError."""
        with self.assertRaises(ToolValidationError):
            validate_save_note_inputs(title="Valid Title", content="")

    def test_path_traversal_in_title_fails(self):
        """Security/Failure case: Path traversal attempts must be rejected."""
        dangerous_titles = [
            "../../etc/passwd",
            "notes/../../secret",
            "file\\nested\\name",
            "test\0bad",
            "file:name",
        ]
        for bad_title in dangerous_titles:
            with self.subTest(bad_title=bad_title):
                with self.assertRaises(ToolValidationError):
                    validate_save_note_inputs(title=bad_title, content="Some content")

    def test_invalid_category_fails(self):
        """Failure case: Categories with spaces or illegal symbols fail."""
        with self.assertRaises(ToolValidationError):
            validate_save_note_inputs(
                title="Notes",
                content="Content",
                category="invalid category!@#",
            )

    def test_output_validation_missing_file_fails(self):
        """Failure case: Output validation raises error if file does not exist."""
        with self.assertRaises(ToolValidationError):
            validate_save_note_output({
                "status": "success",
                "file_path": "/non/existent/path/note.txt",
                "bytes_written": 100,
            })


class TestToolExecution(unittest.TestCase):
    """Tests file writing, security, and output validation."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_note_normal_execution(self):
        """Normal case: Note is saved and verified on disk."""
        result = save_note(
            title="agent_concepts",
            content="Agents use tools, maintain state, and reason.",
            category="study",
            base_dir=self.temp_dir,
        )
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(result["file_path"]))
        self.assertGreater(result["bytes_written"], 0)

        with open(result["file_path"], "r", encoding="utf-8") as f:
            saved_text = f.read()
        self.assertIn("agent_concepts", saved_text)
        self.assertIn("Agents use tools", saved_text)

    def test_save_note_handles_invalid_input_gracefully(self):
        """Failure case: Tool catches validation errors and returns structured error dict without crashing."""
        result = save_note(
            title="../secret_file",
            content="Testing hack",
            base_dir=self.temp_dir,
        )
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "ValidationError")
        self.assertIn("invalid or unsafe characters", result["message"])


class TestAIAgent(unittest.TestCase):
    """Tests Agent behavior, tool decisions, human approval, loop limits, and reasoning."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.agent = AIAgent(
            api_key=None,  # Tests deterministic offline flow & guards without external network
            notes_dir=self.temp_dir,
            require_approval=True,
        )

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_direct_query_no_tool_decision(self):
        """Normal case: General queries do NOT invoke the tool."""
        result = self.agent.run("What is machine learning?")
        self.assertEqual(result.status, AgentState.COMPLETED)
        self.assertEqual(result.tool_calls_count, 0)
        self.assertIsNone(result.pending_action)
        # Verify agent explains why it did what it did
        self.assertTrue(any("No save request detected" in step for step in result.explanation_trail))

    def test_tool_decision_and_approval_workflow(self):
        """Normal case: Save request triggers tool, pauses for approval, executes upon approval."""
        prompt = "Save a note: My first Agentic AI experiment was successful!"
        result = self.agent.run(prompt)

        # 1. Verify agent paused for human approval
        self.assertEqual(result.status, AgentState.AWAITING_APPROVAL)
        self.assertIsNotNone(result.pending_action)
        self.assertEqual(result.pending_action["tool"], "save_note")
        self.assertTrue(any("Human approval required" in step for step in result.explanation_trail))

        # 2. Simulate User Approving the action
        resumed_result = self.agent.resume_with_approval(
            approved=True,
            continuation_context=result.continuation_context,
        )

        self.assertEqual(resumed_result.status, AgentState.COMPLETED)
        self.assertTrue(any("User approved" in step for step in resumed_result.explanation_trail))
        self.assertTrue(any("Verified file created" in step for step in resumed_result.explanation_trail))

        # Verify file is actually on disk
        saved_files = os.listdir(self.temp_dir)
        self.assertEqual(len(saved_files), 1)

    def test_human_approval_rejection_workflow(self):
        """Failure/Safety case: User rejects action -> file is NOT created."""
        prompt = "Save note: This is an unapproved sensitive draft"
        result = self.agent.run(prompt)
        self.assertEqual(result.status, AgentState.AWAITING_APPROVAL)

        # Simulate User Rejecting the action
        resumed_result = self.agent.resume_with_approval(
            approved=False,
            continuation_context=result.continuation_context,
        )

        self.assertEqual(resumed_result.status, AgentState.COMPLETED)
        self.assertIn("cancelled", resumed_result.response_text.lower())
        self.assertTrue(any("User denied approval" in step for step in resumed_result.explanation_trail))

        # Verify NO file was created on disk
        saved_files = os.listdir(self.temp_dir)
        self.assertEqual(len(saved_files), 0)

    def test_max_tool_calls_guardrail(self):
        """Safety case: Guardrail halts execution if tool calls exceed limit (5)."""
        mock_context = {
            "trail": ["Step 1", "Step 2"],
            "tool_calls_count": 6,  # Exceeds max 5
            "func_name": "save_note",
            "validated_inputs": {"title": "overflow", "content": "data", "category": "general"},
        }
        result = self.agent.resume_with_approval(
            approved=True,
            continuation_context=mock_context,
        )
        self.assertEqual(result.status, AgentState.MAX_CALLS_REACHED)
        self.assertIn("safety limit of 5", result.response_text.lower())
        self.assertTrue(any("Guardrail trigger" in step for step in result.explanation_trail))

    def test_agent_handles_runtime_failure_without_crashing(self):
        """Robustness: Invalid input halts gracefully with explanation trail."""
        # Run agent with invalid input that triggers validation error
        prompt = "Save note ../../forbidden/passwd: Secret contents"
        result = self.agent.run(prompt)
        # Should return an error result or safe sanitized fallback without raising unhandled exceptions
        self.assertIn(result.status, [AgentState.ERROR, AgentState.AWAITING_APPROVAL])
        self.assertIsNotNone(result.explanation_trail)


if __name__ == "__main__":
    unittest.main()
