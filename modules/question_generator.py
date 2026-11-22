
import json
import time
from google.genai import types
from config import client, MODEL_NAME
from prompts.generation import GENERATION_PROMPT_V1


def _is_retryable_error(error):
    status_code = getattr(error, "status_code", None)

    if status_code is not None:
        return status_code in (408, 429) or 500 <= status_code < 600

    message = str(error).lower()
    retryable_markers = (
        "timeout",
        "timed out",
        "temporarily",
        "unavailable",
        "overloaded",
        "high demand",
        "connection",
        "network",
        "rate limit",
        "resource exhausted",
        "429",
        "503",
        "502",
        "500",
    )

    return any(marker in message for marker in retryable_markers)


def generate_questions(
    study_material,
    topic,
    difficulty,
    question_type,
    num_questions,
    progress_callback=None,
    max_attempts=5,
):

    prompt = GENERATION_PROMPT_V1.format(
        study_material=study_material,
        topic=topic,
        difficulty=difficulty,
        question_type=question_type,
        num_questions=num_questions
    )

    last_error = None

    for attempt in range(1, max_attempts + 1):
        if progress_callback:
            progress_callback(attempt, max_attempts)

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)

            if "questions" not in result:
                raise ValueError("Invalid response format from Gemini.")

            if not isinstance(result["questions"], list):
                raise ValueError("Questions must be returned as a list.")

            return result

        except (json.JSONDecodeError, ValueError) as error:
            last_error = error

            if attempt >= max_attempts:
                break

            delay = 2 ** attempt
            if progress_callback:
                progress_callback(
                    attempt,
                    max_attempts,
                    f"Invalid response received. Retrying in {delay} seconds..."
                )
            time.sleep(delay)

        except Exception as error:
            last_error = error

            if attempt >= max_attempts or not _is_retryable_error(error):
                break

            delay = 2 ** attempt
            if progress_callback:
                progress_callback(
                    attempt,
                    max_attempts,
                    f"Gemini did not respond. Retrying in {delay} seconds..."
                )
            time.sleep(delay)

    raise last_error
