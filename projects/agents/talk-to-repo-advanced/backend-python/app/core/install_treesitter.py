"""Run once after installing requirements to make sure tree-sitter grammars
for the supported languages are downloaded and buildable."""

from tree_sitter_languages import get_parser

LANGUAGES = ["javascript", "typescript", "python"]

if __name__ == "__main__":
    for lang in LANGUAGES:
        try:
            get_parser(lang)
            print(f"{lang} parser ok")
        except Exception as exc:
            print(f"{lang} failed: {exc}")
