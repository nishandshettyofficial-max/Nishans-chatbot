"""
agent.py
Core AI Agent implementation with:
- Access to one clearly defined tool (`save_note`)
- Tool selection decision (via Gemini or OpenAI models, or offline rules)
- Dual-provider auto-detection (Gemini AIza... or OpenAI sk-...)
- Input and output validation
- Transparent step-by-step reasoning/explanation trail
- Guardrail: Maximum 5 tool calls per task
- Crash-proof error handling
- Human-in-the-loop approval protocol before external actions
"""

import json
import os
from typing import Any, Callable, Dict, List, Optional
from tools import (
    CREATE_DOCUMENT_DECLARATION,
    OPENAI_CREATE_DOCUMENT_TOOL,
    OPENAI_SAVE_NOTE_TOOL,
    SAVE_NOTE_DECLARATION,
    ToolValidationError,
    create_document,
    save_note,
    validate_save_note_inputs,
    validate_save_note_output,
)

# Optional import of google-genai
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
    types = None
    genai = None

# Optional import of openai
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAI = None


class AgentState:
    COMPLETED = "completed"
    AWAITING_APPROVAL = "awaiting_approval"
    ERROR = "error"
    MAX_CALLS_REACHED = "max_calls_reached"


class AgentResult:
    """Represents the structured result returned by the agent."""

    def __init__(
        self,
        status: str,
        response_text: str,
        explanation_trail: List[str],
        tool_calls_count: int = 0,
        pending_action: Optional[Dict[str, Any]] = None,
        continuation_context: Optional[Dict[str, Any]] = None,
        file_info: Optional[Dict[str, Any]] = None,
    ):
        self.status = status
        self.response_text = response_text
        self.explanation_trail = explanation_trail
        self.tool_calls_count = tool_calls_count
        self.pending_action = pending_action
        self.continuation_context = continuation_context
        self.file_info = file_info

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "response_text": self.response_text,
            "explanation_trail": self.explanation_trail,
            "tool_calls_count": self.tool_calls_count,
            "pending_action": self.pending_action,
            "file_info": self.file_info,
        }



class AIAgent:
    """
    Autonomous AI Agent with Human-In-The-Loop approval, loop limits,
    strict validation, and transparent reasoning.
    Supports both Google Gemini and OpenAI providers seamlessly.
    """

    MAX_TOOL_CALLS = 5

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        require_approval: bool = False,
        notes_dir: Optional[str] = None,
    ):
        raw_key = api_key or os.getenv("GEMINI_API_KEY")
        self.api_key = raw_key.strip() if raw_key else None
        self.require_approval = require_approval
        self.notes_dir = notes_dir

        # Auto-detect provider based on key format
        if self.api_key and (self.api_key.startswith("sk-") or self.api_key.startswith("org-")):
            self.provider = "openai"
            self.model_name = model_name or "gpt-4o-mini"
            self.client = OpenAI(api_key=self.api_key) if HAS_OPENAI else None
        elif self.api_key and not self.api_key.startswith("sk-"):
            self.provider = "gemini"
            self.model_name = model_name or "gemini-3.5-flash-lite"
            self.client = genai.Client(api_key=self.api_key) if HAS_GENAI else None


        elif self.api_key:
            # Fallback provider selection
            if HAS_OPENAI and "gpt" in (model_name or ""):
                self.provider = "openai"
                self.model_name = model_name or "gpt-4o-mini"
                self.client = OpenAI(api_key=self.api_key)
            else:
                self.provider = "gemini"
                self.model_name = model_name or "gemini-2.5-flash"
                self.client = genai.Client(api_key=self.api_key) if HAS_GENAI else None
        else:
            self.provider = "offline"
            self.model_name = model_name or "offline-rule-engine"
            self.client = None

    def run(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> AgentResult:
        """
        Executes a user task.
        - Decides whether to use `save_note` or answer directly.
        - If an external action is needed and `require_approval` is True,
          pauses and returns AWAITING_APPROVAL.
        """
        trail: List[str] = []
        trail.append(f"📥 Received user request: '{prompt}'")

        if self.provider == "offline" or not self.client:
            return self._run_offline_agent(prompt, conversation_history, trail)

        if self.provider == "openai":
            return self._run_openai_agent(prompt, conversation_history, trail)
        else:
            return self._run_gemini_agent(prompt, conversation_history, trail)

    def _run_openai_agent(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict[str, str]]],
        trail: List[str],
    ) -> AgentResult:
        """Executes agent workflow via OpenAI API."""
        trail.append(f"🤖 Connected to OpenAI provider (Model: {self.model_name}).")
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Nishan's intelligent personal assistant and creative workspace companion.\n"
                    "You have access to two tools:\n"
                    "1. create_document: Creates, formats, and saves a complete document (such as a Microsoft Word .docx file, essay, report, article, or guide) for any topic requested by the user, making it ready for instant download. ALWAYS call this tool when the user asks to create, make, generate, or write a Word document, docx, report, paper, or file on a topic (e.g. 'can you make a word doc for a topic home'). Use doc_type='docx' for Word documents. Format the content with rich headings (#, ##), bullet points, and insightful paragraphs.\n"
                    "2. save_note: Saves a quick thought, note, or reminder.\n\n"
                    "CRITICAL RULES:\n"
                    "- When asked to make a Word doc or document, ALWAYS invoke create_document. Do NOT refuse or say you cannot generate .docx files!\n"
                    "- After creating the document, provide a concise, friendly, and elegant summary of what you created and inform the user they can download it below. Do NOT paste a massive, repetitive wall of text into the chat once you've already generated the document.\n"
                    "- For standard conversational questions, thoughts, or advice that do not ask for files or notes, answer directly without calling tools."
                ),
            }
        ]

        if conversation_history:
            for msg in conversation_history:
                role = "user" if msg.get("role") == "user" else "assistant"
                messages.append({"role": role, "content": msg.get("content", "")})

        messages.append({"role": "user", "content": prompt})

        try:
            trail.append("🤔 Evaluating request and deciding if tools are needed...")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=[OPENAI_CREATE_DOCUMENT_TOOL, OPENAI_SAVE_NOTE_TOOL],
                tool_choice="auto",
            )
            msg = response.choices[0].message

            if not msg.tool_calls:
                trail.append("💡 Decision: No tool required. Generating direct response.")
                return AgentResult(
                    status=AgentState.COMPLETED,
                    response_text=msg.content or "I have processed your request.",
                    explanation_trail=trail,
                    tool_calls_count=0,
                )

            # Model decided to call a tool
            tc = msg.tool_calls[0]
            func_name = tc.function.name
            func_args = json.loads(tc.function.arguments)

            trail.append(f"🛠️ Model decided to call tool: '{func_name}'")
            trail.append(f"🔍 Validating proposed tool inputs: {func_args}")

            try:
                validated_inputs = validate_save_note_inputs(
                    title=func_args.get("title", "Document"),
                    content=func_args.get("content", ""),
                    category=func_args.get("category", "general"),
                )
                if "doc_type" in func_args:
                    validated_inputs["doc_type"] = func_args["doc_type"]
                trail.append("✅ Tool input validation passed.")
            except ToolValidationError as ve:
                trail.append(f"❌ Tool input validation failed: {str(ve)}")
                return AgentResult(
                    status=AgentState.ERROR,
                    response_text=f"Agent stopped tool execution because the input was invalid: {str(ve)}",
                    explanation_trail=trail,
                    tool_calls_count=1,
                )

            if self.require_approval:
                trail.append("⏸️ Pausing execution: Human approval required before performing external action (saving file).")
                continuation_context = {
                    "provider": "openai",
                    "messages": messages,
                    "model_message": msg,
                    "tool_call": tc,
                    "func_name": func_name,
                    "validated_inputs": validated_inputs,
                    "tool_calls_count": 1,
                    "trail": trail,
                }
                return AgentResult(
                    status=AgentState.AWAITING_APPROVAL,
                    response_text="Action requires your approval to proceed with saving the file to your computer.",
                    explanation_trail=trail,
                    tool_calls_count=1,
                    pending_action={
                        "tool": func_name,
                        "title": validated_inputs["title"],
                        "category": validated_inputs.get("category", "general"),
                        "content_preview": (
                            validated_inputs["content"][:200] + "..."
                            if len(validated_inputs["content"]) > 200
                            else validated_inputs["content"]
                        ),
                        "args": validated_inputs,
                    },
                    continuation_context=continuation_context,
                )

            return self._execute_openai_continue(
                func_name=func_name,
                validated_inputs=validated_inputs,
                messages=messages,
                model_message=msg,
                tool_call=tc,
                tool_calls_count=1,
                trail=trail,
                approved=True,
            )

        except Exception as e:
            trail.append(f"⚠️ Error during OpenAI call: {str(e)}")
            return AgentResult(
                status=AgentState.ERROR,
                response_text=f"An error occurred: {str(e)}",
                explanation_trail=trail,
                tool_calls_count=0,
            )

    def _execute_openai_continue(
        self,
        func_name: str,
        validated_inputs: Dict[str, Any],
        messages: List[Any],
        model_message: Any,
        tool_call: Any,
        tool_calls_count: int,
        trail: List[str],
        approved: bool,
    ) -> AgentResult:
        try:
            trail.append(f"⚡ Executing tool '{func_name}'...")
            file_info = None
            if func_name == "create_document":
                result = create_document(
                    title=validated_inputs["title"],
                    content=validated_inputs["content"],
                    doc_type=validated_inputs.get("doc_type", "docx"),
                    base_dir=self.notes_dir,
                )
            else:
                result = save_note(
                    title=validated_inputs["title"],
                    content=validated_inputs["content"],
                    category=validated_inputs.get("category", "general"),
                    base_dir=self.notes_dir,
                )

            if result.get("status") == "success":
                validate_save_note_output(result)
                file_info = {
                    "file_path": result.get("file_path"),
                    "filename": result.get("filename"),
                    "doc_type": result.get("doc_type", "docx"),
                    "bytes_written": result.get("bytes_written"),
                }
                trail.append(f"📁 Verified file created on disk: {result['file_path']} ({result['bytes_written']} bytes)")
            else:
                trail.append(f"⚠️ Tool error: {result.get('message')}")

            # Send tool response back to OpenAI
            updated_messages = list(messages)
            updated_messages.append(model_message)
            updated_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })

            synth_resp = self.client.chat.completions.create(
                model=self.model_name,
                messages=updated_messages,
            )
            final_text = synth_resp.choices[0].message.content or result["message"]
            trail.append("🏁 Completed task successfully.")
            return AgentResult(
                status=AgentState.COMPLETED,
                response_text=final_text,
                explanation_trail=trail,
                tool_calls_count=tool_calls_count,
                file_info=file_info,
            )
        except Exception as e:
            trail.append(f"❌ Execution error: {str(e)}")
            return AgentResult(
                status=AgentState.ERROR,
                response_text=f"Error during tool execution: {str(e)}",
                explanation_trail=trail,
                tool_calls_count=tool_calls_count,
            )


    def _gemini_generate_with_fallback(
        self,
        contents: Any,
        config: Optional[Any] = None,
    ) -> Any:
        """Attempts generation with primary model, falling back to alternates if 503 or 404 occurs."""
        candidate_models = [self.model_name]
        for fallback in ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"]:
            if fallback not in candidate_models:
                candidate_models.append(fallback)

        last_error = None
        for model in candidate_models:
            try:
                if config is not None:
                    return self.client.models.generate_content(
                        model=model,
                        contents=contents,
                        config=config,
                    )
                else:
                    return self.client.models.generate_content(
                        model=model,
                        contents=contents,
                    )
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                if "503" in err_str or "404" in err_str or "unavailable" in err_str or "demand" in err_str:
                    continue
                raise e
        if last_error:
            raise last_error

    def _run_gemini_agent(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict[str, str]]],
        trail: List[str],
    ) -> AgentResult:
        """Executes agent workflow via Gemini API."""
        trail.append(f"🤖 Connected to Gemini provider (Model: {self.model_name}).")
        
        create_doc_func_decl = types.FunctionDeclaration(
            name=CREATE_DOCUMENT_DECLARATION["name"],
            description=CREATE_DOCUMENT_DECLARATION["description"],
            parameters=CREATE_DOCUMENT_DECLARATION["parameters"],
        )
        save_note_func_decl = types.FunctionDeclaration(
            name=SAVE_NOTE_DECLARATION["name"],
            description=SAVE_NOTE_DECLARATION["description"],
            parameters=SAVE_NOTE_DECLARATION["parameters"],
        )
        gemini_tool = types.Tool(function_declarations=[create_doc_func_decl, save_note_func_decl])

        contents = []
        if conversation_history:
            for msg in conversation_history:
                role = "user" if msg.get("role") == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg.get("content", ""))],
                    )
                )

        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            )
        )

        try:
            trail.append("🤔 Evaluating request and deciding if tools are needed...")
            response = self._gemini_generate_with_fallback(
                contents=contents,
                config=types.GenerateContentConfig(
                    tools=[gemini_tool],
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=True
                    ),
                    system_instruction=(
                        "You are Nishan's intelligent personal assistant and creative workspace companion.\n"
                        "You have access to two tools:\n"
                        "1. `create_document`: Creates, formats, and saves a complete document (such as a Microsoft Word .docx file, essay, report, article, or guide) for any topic requested by the user, making it ready for instant download. ALWAYS call this tool when the user asks to create, make, generate, or write a Word document, docx, report, paper, or file on a topic (e.g. 'can you make a word doc for a topic home'). Use doc_type='docx' for Word documents. Format the content with rich headings (#, ##), bullet points, and insightful paragraphs.\n"
                        "2. `save_note`: Saves a quick thought, note, or reminder to disk.\n\n"
                        "IMPORTANT INSTRUCTIONS:\n"
                        "- When asked to make a Word doc or document, ALWAYS invoke create_document. Do NOT refuse or claim you cannot generate .docx files, because you CAN!\n"
                        "- After creating the document, provide a concise, friendly, and elegant summary of what you created and inform the user they can download it directly below. Do NOT paste a massive, repetitive wall of text into the chat once you've already generated the document.\n"
                        "- For standard conversational questions, thoughts, or advice that do not ask for files or notes, answer directly without calling tools.\n"
                        "- Keep your tone professional, articulate, helpful, and Apple-refined."
                    ),
                ),
            )

            function_calls = getattr(response, "function_calls", None)
            if not function_calls:
                trail.append("💡 Decision: No tool required. Generating direct response.")
                return AgentResult(
                    status=AgentState.COMPLETED,
                    response_text=response.text or "I have processed your request.",
                    explanation_trail=trail,
                    tool_calls_count=0,
                )

            fc = function_calls[0]
            func_name = fc.name
            func_args = dict(fc.args) if hasattr(fc, "args") else {}

            trail.append(f"🛠️ Model decided to call tool: '{func_name}'")
            trail.append(f"🔍 Validating proposed tool inputs: {func_args}")

            try:
                validated_inputs = validate_save_note_inputs(
                    title=func_args.get("title", "Document"),
                    content=func_args.get("content", ""),
                    category=func_args.get("category", "general"),
                )
                if "doc_type" in func_args:
                    validated_inputs["doc_type"] = func_args["doc_type"]
                trail.append("✅ Tool input validation passed.")
            except ToolValidationError as ve:
                trail.append(f"❌ Tool input validation failed: {str(ve)}")
                return AgentResult(
                    status=AgentState.ERROR,
                    response_text=f"Agent stopped tool execution because the input was invalid: {str(ve)}",
                    explanation_trail=trail,
                    tool_calls_count=1,
                )

            if self.require_approval:
                trail.append("⏸️ Pausing execution: Human approval required before performing external action (saving file).")
                continuation_context = {
                    "provider": "gemini",
                    "contents": contents,
                    "model_call_content": response.candidates[0].content,
                    "func_name": func_name,
                    "validated_inputs": validated_inputs,
                    "tool_calls_count": 1,
                    "trail": trail,
                }
                return AgentResult(
                    status=AgentState.AWAITING_APPROVAL,
                    response_text="Action requires your approval to proceed with saving the file to your computer.",
                    explanation_trail=trail,
                    tool_calls_count=1,
                    pending_action={
                        "tool": func_name,
                        "title": validated_inputs["title"],
                        "category": validated_inputs.get("category", "general"),
                        "content_preview": (
                            validated_inputs["content"][:200] + "..."
                            if len(validated_inputs["content"]) > 200
                            else validated_inputs["content"]
                        ),
                        "args": validated_inputs,
                    },
                    continuation_context=continuation_context,
                )

            return self._execute_gemini_continue(
                func_name=func_name,
                validated_inputs=validated_inputs,
                contents=contents,
                model_call_content=response.candidates[0].content,
                tool_calls_count=1,
                trail=trail,
                approved=True,
            )

        except Exception as e:
            trail.append(f"⚠️ Encountered error during Gemini call: {str(e)}")
            return AgentResult(
                status=AgentState.ERROR,
                response_text=f"An error occurred: {str(e)}",
                explanation_trail=trail,
                tool_calls_count=0,
            )

    def _execute_gemini_continue(
        self,
        func_name: str,
        validated_inputs: Dict[str, Any],
        contents: List[Any],
        model_call_content: Any,
        tool_calls_count: int,
        trail: List[str],
        approved: bool,
    ) -> AgentResult:
        try:
            trail.append(f"⚡ Executing tool '{func_name}'...")
            file_info = None
            if func_name == "create_document":
                result = create_document(
                    title=validated_inputs["title"],
                    content=validated_inputs["content"],
                    doc_type=validated_inputs.get("doc_type", "docx"),
                    base_dir=self.notes_dir,
                )
            else:
                result = save_note(
                    title=validated_inputs["title"],
                    content=validated_inputs["content"],
                    category=validated_inputs.get("category", "general"),
                    base_dir=self.notes_dir,
                )

            if result.get("status") == "success":
                validate_save_note_output(result)
                file_info = {
                    "file_path": result.get("file_path"),
                    "filename": result.get("filename"),
                    "doc_type": result.get("doc_type", "docx"),
                    "bytes_written": result.get("bytes_written"),
                }
                trail.append(f"📁 Verified file created on disk: {result['file_path']} ({result['bytes_written']} bytes)")
            else:
                trail.append(f"⚠️ Tool reported error: {result.get('message')}")

            if self.client and model_call_content:
                tool_response_part = types.Part.from_function_response(
                    name=func_name,
                    response=result,
                )
                tool_content = types.Content(role="user", parts=[tool_response_part])
                all_contents = contents + [model_call_content, tool_content]
                final_response = self._gemini_generate_with_fallback(
                    contents=all_contents,
                )

                response_text = final_response.text or result["message"]
            else:
                response_text = result["message"]

            trail.append("🏁 Completed task successfully.")
            return AgentResult(
                status=AgentState.COMPLETED,
                response_text=response_text,
                explanation_trail=trail,
                tool_calls_count=tool_calls_count,
                file_info=file_info,
            )
        except Exception as e:
            trail.append(f"❌ Execution error: {str(e)}")
            return AgentResult(
                status=AgentState.ERROR,
                response_text=f"Error executing tool: {str(e)}",
                explanation_trail=trail,
                tool_calls_count=tool_calls_count,
            )

    def resume_with_approval(
        self,
        approved: bool,
        continuation_context: Dict[str, Any],
    ) -> AgentResult:
        """Resumes paused task after user grants or denies approval."""
        trail = continuation_context.get("trail", [])
        tool_calls_count = continuation_context.get("tool_calls_count", 1)
        provider = continuation_context.get("provider", "offline")

        if tool_calls_count > self.MAX_TOOL_CALLS:
            trail.append(f"🛑 Guardrail trigger: Exceeded maximum allowed tool calls ({self.MAX_TOOL_CALLS}). Halting.")
            return AgentResult(
                status=AgentState.MAX_CALLS_REACHED,
                response_text=f"Execution halted: Reached safety limit of {self.MAX_TOOL_CALLS} tool calls for this task.",
                explanation_trail=trail,
                tool_calls_count=tool_calls_count,
            )

        if not approved:
            trail.append("🚫 User denied approval for external action. Aborting file write.")
            return AgentResult(
                status=AgentState.COMPLETED,
                response_text="Action cancelled: The file was not saved to your computer.",
                explanation_trail=trail,
                tool_calls_count=tool_calls_count,
            )

        trail.append("✅ User approved external action. Proceeding with file write...")
        validated_inputs = continuation_context["validated_inputs"]
        func_name = continuation_context["func_name"]

        if provider == "openai":
            return self._execute_openai_continue(
                func_name=func_name,
                validated_inputs=validated_inputs,
                messages=continuation_context.get("messages", []),
                model_message=continuation_context.get("model_message"),
                tool_call=continuation_context.get("tool_call"),
                tool_calls_count=tool_calls_count,
                trail=trail,
                approved=True,
            )
        elif provider == "gemini":
            return self._execute_gemini_continue(
                func_name=func_name,
                validated_inputs=validated_inputs,
                contents=continuation_context.get("contents", []),
                model_call_content=continuation_context.get("model_call_content"),
                tool_calls_count=tool_calls_count,
                trail=trail,
                approved=True,
            )
        else:
            # Offline execution
            if func_name == "create_document":
                res = create_document(
                    title=validated_inputs["title"],
                    content=validated_inputs["content"],
                    doc_type=validated_inputs.get("doc_type", "docx"),
                    base_dir=self.notes_dir,
                )
            else:
                res = save_note(
                    title=validated_inputs["title"],
                    content=validated_inputs["content"],
                    category=validated_inputs.get("category", "general"),
                    base_dir=self.notes_dir,
                )
            file_info = None
            if res.get("status") == "success":
                validate_save_note_output(res)
                file_info = {
                    "file_path": res.get("file_path"),
                    "filename": res.get("filename"),
                    "doc_type": res.get("doc_type", "docx"),
                    "bytes_written": res.get("bytes_written"),
                }
                trail.append(f"📁 Verified file created on disk: {res['file_path']} ({res['bytes_written']} bytes)")
            else:
                trail.append(f"⚠️ Tool error: {res.get('message')}")
            trail.append("🏁 Completed task successfully.")
            return AgentResult(
                status=AgentState.COMPLETED,
                response_text=res.get("message", "File saved successfully."),
                explanation_trail=trail,
                tool_calls_count=tool_calls_count,
                file_info=file_info,
            )

    def _run_offline_agent(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict[str, str]]],
        trail: List[str],
    ) -> AgentResult:
        """Deterministic local fallback agent when no API key is configured."""
        trail.append("⚠️ Offline Mode: Using local rule-based agent (no active API key detected).")
        prompt_lower = prompt.lower()

        doc_keywords = ["word doc", "word document", "docx", "create doc", "make doc", "document on", "document for"]
        save_keywords = ["save note", "save a note", "save this note", "record note", "create note", "save to file"]

        is_doc = any(kw in prompt_lower for kw in doc_keywords)
        is_note = any(kw in prompt_lower for kw in save_keywords)

        if not is_doc and not is_note:
            trail.append("💡 Decision: No save request detected. Answering query directly.")
            return AgentResult(
                status=AgentState.COMPLETED,
                response_text=(
                    f"I received your question: \"{prompt}\". "
                    "To enable full AI reasoning, please enter your API key in the sidebar or in your .env file."
                ),
                explanation_trail=trail,
                tool_calls_count=0,
            )

        if is_doc:
            trail.append("🛠️ Decision: Detected request to create a document. Invoking 'create_document' tool.")
            title = "Document"
            for kw in doc_keywords:
                if kw in prompt_lower:
                    parts = prompt_lower.split(kw, 1)
                    if len(parts) > 1 and parts[1].strip():
                        raw_t = parts[1].strip().replace("topic", "").strip(": ").strip()
                        title = raw_t.title() or "Document"
                    break
            clean_title = "".join(c for c in title if c.isalnum() or c in ("_", "-"))[:50] or "Document"
            content = f"# {clean_title}\n\nComprehensive exploration and document on {clean_title}.\n\n## Overview\nThis document provides an overview of {clean_title}."

            res = create_document(title=clean_title, content=content, doc_type="docx", base_dir=self.notes_dir)
            file_info = {
                "file_path": res.get("file_path"),
                "filename": res.get("filename"),
                "doc_type": "docx",
                "bytes_written": res.get("bytes_written"),
            }
            trail.append(f"📁 Output verified: {res.get('message')}")
            trail.append("🏁 Completed task successfully.")
            return AgentResult(
                status=AgentState.COMPLETED,
                response_text=f"I have created a Word document for you on **{clean_title}**. You can download it directly below.",
                explanation_trail=trail,
                tool_calls_count=1,
                file_info=file_info,
            )

        trail.append("🛠️ Decision: Detected request to save a note. Invoking 'save_note' tool.")
        title = "note_" + str(len(trail))
        content = prompt

        if ":" in prompt:
            parts = prompt.split(":", 1)
            title = parts[0].replace("save note", "").replace("save a note", "").strip() or "my_note"
            content = parts[1].strip()

        clean_title = "".join(c for c in title if c.isalnum() or c in ("_", "-"))[:50] or "quick_note"

        try:
            validated = validate_save_note_inputs(title=clean_title, content=content, category="offline")
            trail.append("✅ Tool input validation passed.")
        except ToolValidationError as ve:
            trail.append(f"❌ Tool input validation failed: {str(ve)}")
            return AgentResult(
                status=AgentState.ERROR,
                response_text=f"Invalid note input: {str(ve)}",
                explanation_trail=trail,
                tool_calls_count=1,
            )

        res = save_note(title=validated["title"], content=validated["content"], category="offline", base_dir=self.notes_dir)
        file_info = {
            "file_path": res.get("file_path"),
            "filename": res.get("filename"),
            "doc_type": "md",
            "bytes_written": res.get("bytes_written"),
        }
        trail.append(f"📁 Output verified: {res.get('message')}")
        trail.append("🏁 Completed task successfully.")
        return AgentResult(
            status=AgentState.COMPLETED,
            response_text=res.get("message", "Note saved successfully."),
            explanation_trail=trail,
            tool_calls_count=1,
            file_info=file_info,
        )

