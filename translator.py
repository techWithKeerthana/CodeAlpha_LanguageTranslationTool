"""Utility functions for language translation using deep-translator."""

from __future__ import annotations

from functools import lru_cache

from deep_translator import GoogleTranslator


@lru_cache(maxsize=1)
def get_supported_languages() -> dict[str, str]:
    """Return a sorted mapping of language name -> language code."""
    languages = GoogleTranslator().get_supported_languages(as_dict=True)
    return dict(sorted(languages.items(), key=lambda item: item[0]))


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Translate text from source language code to target language code.

    Raises:
        ValueError: For invalid user input.
        RuntimeError: For network/API related translation failures.
    """
    cleaned_text = text.strip()
    if not cleaned_text:
        raise ValueError("Please enter text to translate.")

    if source_lang == target_lang and source_lang != "auto":
        raise ValueError("Source and target languages cannot be the same.")

    supported_codes = set(get_supported_languages().values())

    if source_lang != "auto" and source_lang not in supported_codes:
        raise ValueError("Unsupported source language selected.")

    if target_lang not in supported_codes:
        raise ValueError("Unsupported target language selected.")

    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(cleaned_text)
    except Exception as exc:
        raise RuntimeError(
            "Translation failed. Check your internet connection and try again."
        ) from exc

    if not translated:
        raise RuntimeError("Translation service returned an empty response.")

    return translated
