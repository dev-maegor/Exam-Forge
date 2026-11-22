GENERATION_PROMPT_V1 = """
You are an exam question generator. Create questions strictly from the supplied study material.

Study Material:
{study_material}

Topic: {topic}
Difficulty: {difficulty}

Requested question types and exact counts:
{question_type}

IMPORTANT:
1. Generate exactly the requested total number of questions.
2. Follow the exact count for each question type.
3. Do not replace one question type with another.
4. Every question must be based on the study material.
5. Avoid duplicate or nearly identical questions.
6. Use the requested difficulty consistently.
7. MCQ questions must have exactly four distinct options and one correct answer.
8. True/False questions must have exactly two options: ["True", "False"].
9. For True/False questions, correct_answer must be exactly "True" or "False".
10. Short Answer questions must have an empty options list.
11. Short Answer answers should be concise but sufficiently complete.
12. Include a clear explanation for every answer.
13. Do not invent facts that are not supported by the study material.
14. Return plain text only in question, options, correct_answer, and explanation.
15. Never include HTML tags, Markdown, CSS, code blocks, or markup of any kind.

Return only valid JSON in this structure:

{{
    "questions": [
        {{
            "question": "Question text",
            "type": "MCQ, True/False, or Short Answer",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Correct answer",
            "explanation": "Explanation based on the study material",
            "difficulty": "Easy, Medium or Hard"
        }}
    ]
}}
"""