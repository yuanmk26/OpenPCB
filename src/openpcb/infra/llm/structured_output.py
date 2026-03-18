from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError


class StructuredOutputError(Exception):
    """
    Base exception for structured output parsing errors.
    """


class StructuredOutputFormatError(StructuredOutputError):
    """
    Raised when the model output is not valid JSON or cannot be decoded.
    """


class StructuredOutputValidationError(StructuredOutputError):
    """
    Raised when decoded JSON does not satisfy the target schema.
    """


TModel = TypeVar("TModel", bound=BaseModel)


@dataclass(slots=True)
class ParsedStructuredOutput:
    """
    Normalized structured-output parsing result.

    Attributes:
        data:
            The validated Python object. Usually a dict or a Pydantic model.
        raw_text:
            Original raw text returned by the LLM.
        json_data:
            The decoded JSON object before final schema validation/coercion.
    """

    data: Any
    raw_text: str
    json_data: Any


class StructuredOutputParser:
    """
    Utility for converting LLM text outputs into validated structured objects.

    Current responsibilities:
    1. Extract JSON text from a raw model response
    2. Decode JSON safely
    3. Validate/coerce it into either:
       - plain Python dict/list output
       - a specific Pydantic model
    """

    def parse_json_object(self, text: str) -> ParsedStructuredOutput:
        """
        Parse raw LLM text into a decoded JSON object.

        This method is useful when the caller only needs a Python dict/list
        and will perform validation elsewhere.

        Args:
            text: Raw text content from the LLM.

        Returns:
            ParsedStructuredOutput

        Raises:
            StructuredOutputFormatError:
                If no valid JSON object/array can be extracted.
        """
        cleaned_text = self._extract_json_text(text)
        json_data = self._load_json(cleaned_text)

        return ParsedStructuredOutput(
            data=json_data,
            raw_text=text,
            json_data=json_data,
        )

    def parse_model(self, text: str, model_type: type[TModel]) -> ParsedStructuredOutput:
        """
        Parse raw LLM text into a validated Pydantic model instance.

        Args:
            text: Raw text content from the LLM.
            model_type: Target Pydantic model class.

        Returns:
            ParsedStructuredOutput where `data` is an instance of model_type.

        Raises:
            StructuredOutputFormatError:
                If no valid JSON can be extracted/decoded.
            StructuredOutputValidationError:
                If decoded JSON fails schema validation.
        """
        cleaned_text = self._extract_json_text(text)
        json_data = self._load_json(cleaned_text)

        try:
            model_instance = model_type.model_validate(json_data)
        except ValidationError as exc:
            raise StructuredOutputValidationError(
                f"Structured output validation failed for model {model_type.__name__}: {exc}"
            ) from exc

        return ParsedStructuredOutput(
            data=model_instance,
            raw_text=text,
            json_data=json_data,
        )

    def build_json_response_format(
        self,
        *,
        schema: dict[str, Any],
        name: str = "structured_output",
        strict: bool = True,
    ) -> dict[str, Any]:
        """
        Build an OpenAI-compatible JSON schema response_format payload.

        This helper is optional, but it keeps provider-specific response-format
        construction out of service-layer code.

        Args:
            schema: JSON schema dictionary.
            name: Schema name required by some providers.
            strict: Whether to request strict schema adherence.

        Returns:
            dict: response_format payload to pass into LLMClient.generate(...)
        """
        return {
            "type": "json_schema",
            "json_schema": {
                "name": name,
                "schema": schema,
                "strict": strict,
            },
        }

    def _extract_json_text(self, text: str) -> str:
        """
        Extract a likely JSON payload from raw LLM text.

        Supports these common model behaviors:
        1. Pure JSON text
        2. JSON wrapped in markdown fences
        3. Extra explanation before/after JSON

        Strategy:
        - First try fenced-code extraction if present
        - Otherwise try full text
        - Otherwise fall back to the first balanced JSON object/array slice
        """
        if not isinstance(text, str) or not text.strip():
            raise StructuredOutputFormatError("LLM output is empty.")

        stripped = text.strip()

        fenced = self._extract_from_code_fence(stripped)
        if fenced is not None:
            return fenced

        try:
            json.loads(stripped)
            return stripped
        except json.JSONDecodeError:
            pass

        sliced = self._extract_balanced_json_substring(stripped)
        if sliced is None:
            raise StructuredOutputFormatError(
                "Could not find a valid JSON object or array in LLM output."
            )

        return sliced

    def _load_json(self, text: str) -> Any:
        """
        Decode JSON text into Python data.
        """
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise StructuredOutputFormatError(
                f"Failed to decode JSON from LLM output: {exc}"
            ) from exc

    def _extract_from_code_fence(self, text: str) -> str | None:
        """
        Extract content from a markdown code fence if it looks like JSON.

        Examples:
            ```json
            {...}
            ```

            ```
            {...}
            ```
        """
        if not text.startswith("```"):
            return None

        lines = text.splitlines()
        if len(lines) < 3:
            return None

        first_line = lines[0].strip()
        last_line = lines[-1].strip()

        if not last_line.startswith("```"):
            return None

        if first_line in {"```", "```json", "```JSON"}:
            inner = "\n".join(lines[1:-1]).strip()
            return inner or None

        return None

    def _extract_balanced_json_substring(self, text: str) -> str | None:
        """
        Extract the first balanced top-level JSON object or array substring.

        This is a tolerant fallback for outputs like:
            Here is the result:
            {...}

        or:
            The answer is:
            [ ... ]

        Note:
            This is intentionally simple and aimed at common LLM output shapes.
        """
        start_positions = []
        object_start = text.find("{")
        array_start = text.find("[")

        if object_start != -1:
            start_positions.append(object_start)
        if array_start != -1:
            start_positions.append(array_start)

        if not start_positions:
            return None

        start = min(start_positions)
        opening = text[start]
        closing = "}" if opening == "{" else "]"

        depth = 0
        in_string = False
        escape = False

        for index in range(start, len(text)):
            char = text[index]

            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
                continue

            if char == opening:
                depth += 1
            elif char == closing:
                depth -= 1
                if depth == 0:
                    return text[start : index + 1]

        return None