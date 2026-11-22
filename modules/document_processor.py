
import io
import re
import pymupdf


def extract_text(file_name, file_bytes, progress_callback=None):
    extension = file_name.lower().split(".")[-1]

    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    if extension == "pdf":
        document = pymupdf.open(
            stream=io.BytesIO(file_bytes),
            filetype="pdf"
        )

        try:
            pages = []
            total_pages = document.page_count

            for page_number, page in enumerate(document, start=1):
                pages.append(page.get_text())

                if progress_callback:
                    progress_callback(page_number, total_pages)

            text = "\n".join(pages)
        finally:
            document.close()

    elif extension == "txt":
        text = file_bytes.decode("utf-8-sig")

    else:
        raise ValueError("Only PDF and TXT files are supported.")

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    if not text:
        raise ValueError(
            "No readable text found in the document."
        )

    return text
