
import json
import time
import re
import html
from google.genai import types
from config import client, MODEL_NAME
from prompts.generation_v3 import GENERATION_PROMPT_V3


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


def _sanitize_plain_text(value):
    if value is None:
        return ""

    text = html.unescape(str(value))

    artifact_markers = (
        "```",
        "~~~",
        "<div",
        "<span",
        "<p",
        "<br",
        "&lt;div",
        "&lt;span",
    )
    for marker in artifact_markers:
        marker_index = text.find(marker)
        if marker_index >= 0:
            text = text[:marker_index]

    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"~~~.*?~~~", " ", text, flags=re.DOTALL)
    text = re.sub(r"```[\w]*|~~~[\w]*", " ", text)
    text = text.replace("`", "")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _sanitize_generated_questions(result):
    questions = result.get("questions")

    if not isinstance(questions, list):
        return result

    for question in questions:
        if not isinstance(question, dict):
            continue

        raw_answer = str(question.get("correct_answer") or "")
        raw_explanation = str(question.get("explanation") or "")

        answer_match = re.search(
            r'class=["\']ef-solution-answer["\'][^>]*>(.*?)</[^>]+>',
            raw_answer,
            flags=re.DOTALL | re.IGNORECASE,
        )
        explanation_match = re.search(
            r'class=["\']ef-solution-explanation["\'][^>]*>(.*?)</[^>]+>',
            raw_explanation,
            flags=re.DOTALL | re.IGNORECASE,
        )

        if answer_match:
            raw_answer = answer_match.group(1)
        if explanation_match:
            raw_explanation = explanation_match.group(1)

        question["question"] = _sanitize_plain_text(question.get("question"))
        question["correct_answer"] = _sanitize_plain_text(raw_answer)
        question["explanation"] = _sanitize_plain_text(raw_explanation)

        options = question.get("options")
        if isinstance(options, list):
            question["options"] = [
                _sanitize_plain_text(option)
                for option in options
                if _sanitize_plain_text(option)
            ]

    return result


def sanitize_generated_questions(result):
    return _sanitize_generated_questions(result)


def generate_questions(
    study_material,
    topic,
    difficulty,
    question_type,
    num_questions,
    progress_callback=None,
    max_attempts=5,
):

    prompt = GENERATION_PROMPT_V3.format(
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

            return _sanitize_generated_questions(result)

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
