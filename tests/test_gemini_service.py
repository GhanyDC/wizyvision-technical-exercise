from google.genai import types

from app.gemini_service import GeminiService


def test_parse_agentic_response_builds_timeline() -> None:
    service = GeminiService(
        api_key="test-key",
        model_name="gemini-2.5-flash",
        agentic_model_name="gemini-3-flash-preview",
        timeout_seconds=30,
    )
    response = types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part(text="Need a closer look at the label.", thought=True),
                        types.Part(
                            executable_code=types.ExecutableCode(
                                code="print('zoom label')",
                                language=types.Language.PYTHON,
                            )
                        ),
                        types.Part(
                            code_execution_result=types.CodeExecutionResult(
                                output="zoom label",
                                outcome=types.Outcome.OUTCOME_OK,
                            )
                        ),
                        types.Part(
                            inline_data=types.Blob(
                                data=b"annotated-image",
                                mime_type="image/png",
                            )
                        ),
                        types.Part(text="The serial number appears to be SN-2481-AX9."),
                    ],
                )
            )
        ]
    )

    result = service._parse_agentic_response(response)

    assert result["answer"] == "The serial number appears to be SN-2481-AX9."
    assert result["model"] == "gemini-3-flash-preview"
    assert result["mode"] == "agentic"
    assert result["timeline"] == [
        {
            "type": "think",
            "content": "Need a closer look at the label.",
        },
        {
            "type": "act",
            "language": "python",
            "code": "print('zoom label')",
        },
        {
            "type": "observe",
            "output": "zoom label",
            "outcome": "outcome_ok",
        },
        {
            "type": "image",
            "mime_type": "image/png",
            "data": "YW5ub3RhdGVkLWltYWdl",
        },
    ]
