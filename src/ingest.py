from pathlib import Path
from typing import Dict, Any

class IngestionError(Exception):
    pass

class InputIngester:
    def __init__(self, min_word_count: int = 50):
        self.min_word_count = min_word_count

    def ingest_file(self, file_path: str | Path) -> Dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            raise IngestionError(f"Input file not found: {path}")

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="latin-1")
        except Exception as e:
            raise IngestionError(f"Error reading file {path}: {str(e)}")

        return self.ingest_text(content, source_name=path.name)

    def ingest_text(self, text: str, source_name: str = "raw_text") -> Dict[str, Any]:
        if not text or not text.strip():
            raise IngestionError("Input content is empty.")

        cleaned = " ".join(text.split())
        words = cleaned.split()
        word_count = len(words)

        if word_count < self.min_word_count:
            raise IngestionError(
                f"Input has only {word_count} words. Minimum required is {self.min_word_count} words."
            )

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        title = lines[0].lstrip("#").strip() if lines else "Untitled Source"

        return {
            "source_name": source_name,
            "title": title,
            "raw_text": text,
            "cleaned_text": cleaned,
            "word_count": word_count,
            "estimated_read_minutes": round(word_count / 200.0, 1),
            "paragraphs": [p.strip() for p in text.split("\n\n") if p.strip()],
        }
