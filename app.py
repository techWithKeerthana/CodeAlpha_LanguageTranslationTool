"""Streamlit UI for the CodeAlpha Language Translation Tool."""

from __future__ import annotations

from io import BytesIO

import pyperclip
import streamlit as st
from gtts import gTTS
from gtts.lang import tts_langs

from translator import get_supported_languages, translate_text


def text_to_speech_audio(text: str, lang_code: str) -> bytes:
    """Convert text to speech and return MP3 bytes."""
    buffer = BytesIO()
    tts = gTTS(text=text, lang=lang_code)
    tts.write_to_fp(buffer)
    return buffer.getvalue()


def resolve_tts_language_code(lang_code: str) -> str:
    """Return the closest gTTS-compatible language code."""
    supported_tts_languages = tts_langs()
    normalized_code = lang_code.lower()

    if normalized_code in supported_tts_languages:
        return normalized_code

    base_code = normalized_code.split("-")[0]
    if base_code in supported_tts_languages:
        return base_code

    raise ValueError("Text-to-speech is unavailable for this language.")


def initialize_session_state() -> None:
    """Set default values used by the app."""
    defaults = {
        "input_text": "",
        "source_label": "Auto Detect",
        "target_label": "english",
        "translated_text": "",
        "target_code": "en",
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def clear_translation() -> None:
    """Clear the current input and output text."""
    st.session_state.input_text = ""
    st.session_state.translated_text = ""


def swap_languages(source_options: dict[str, str], target_options: dict[str, str]) -> None:
    """Swap selected source and target languages when possible."""
    if st.session_state.source_label == "Auto Detect":
        st.warning("Choose a specific source language before using Swap.")
        return

    source_label = st.session_state.source_label
    target_label = st.session_state.target_label

    if source_label not in source_options or target_label not in target_options:
        return

    st.session_state.source_label = target_label
    st.session_state.target_label = source_label
    st.session_state.translated_text = ""


def apply_custom_styles() -> None:
    """Add a lightweight visual polish layer."""
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #f4efe6 0%, #fffaf2 45%, #f8f4ed 100%);
        }
        .hero-card {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid #e8dcc8;
            border-radius: 20px;
            padding: 1.4rem 1.5rem;
            box-shadow: 0 16px 40px rgba(92, 67, 39, 0.08);
            margin-bottom: 1rem;
        }
        .hero-title {
            font-size: 2rem;
            font-weight: 700;
            color: #2f2419;
            margin-bottom: 0.35rem;
        }
        .hero-text {
            color: #6b5740;
            font-size: 1rem;
            line-height: 1.5;
        }
        .stButton > button {
            border-radius: 999px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Language Translation Tool", page_icon="🌐")
    apply_custom_styles()
    languages = get_supported_languages()
    source_options = {"Auto Detect": "auto", **languages}
    target_options = languages

    initialize_session_state()

    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">Language Translation Tool</div>
            <div class="hero-text">
                Translate text with auto-detect support, copy the result, and listen to the output with text-to-speech.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("CodeAlpha AI Internship - Task 1")

    st.text_area(
        "Enter text",
        key="input_text",
        height=170,
        placeholder="Type or paste the text you want to translate...",
    )

    helper_col1, helper_col2 = st.columns(2)
    helper_col1.caption(f"Characters: {len(st.session_state.input_text.strip())}")
    helper_col2.caption("Tip: Use Auto Detect if you are unsure about the source language.")

    col1, col2 = st.columns(2)
    with col1:
        st.selectbox(
            "Source language",
            list(source_options.keys()),
            key="source_label",
        )
    with col2:
        st.selectbox(
            "Target language",
            list(target_options.keys()),
            key="target_label",
        )

    action_col1, action_col2, action_col3 = st.columns([1.4, 1, 1])
    with action_col1:
        translate_clicked = st.button("Translate", type="primary", use_container_width=True)
    with action_col2:
        st.button(
            "Swap",
            on_click=swap_languages,
            args=(source_options, target_options),
            use_container_width=True,
        )
    with action_col3:
        st.button("Clear", on_click=clear_translation, use_container_width=True)

    if translate_clicked:
        source_code = source_options[st.session_state.source_label]
        target_code = target_options[st.session_state.target_label]

        try:
            st.session_state.translated_text = translate_text(
                text=st.session_state.input_text,
                source_lang=source_code,
                target_lang=target_code,
            )
            st.session_state.target_code = target_code
            st.success("Translation complete.")
        except ValueError as exc:
            st.session_state.translated_text = ""
            st.error(str(exc))
        except RuntimeError as exc:
            st.session_state.translated_text = ""
            st.error(str(exc))

    if st.session_state.translated_text:
        st.subheader("Translated text")
        st.text_area("Output", st.session_state.translated_text, height=170, disabled=True)

        result_col1, result_col2 = st.columns(2)
        result_col1.caption(f"Output characters: {len(st.session_state.translated_text)}")

        tts_available = True
        try:
            tts_code = resolve_tts_language_code(st.session_state.target_code)
        except ValueError:
            tts_available = False
            tts_code = ""

        result_col2.caption(
            "Audio available for this language."
            if tts_available
            else "Audio is not supported for the selected target language."
        )

        output_action_col1, output_action_col2 = st.columns(2)

        with output_action_col1:
            if st.button("Copy to Clipboard"):
                try:
                    pyperclip.copy(st.session_state.translated_text)
                    st.success("Copied translated text to clipboard.")
                except pyperclip.PyperclipException:
                    st.error("Clipboard is not available on this system.")

        with output_action_col2:
            if st.button("Listen", disabled=not tts_available):
                try:
                    audio_bytes = text_to_speech_audio(
                        text=st.session_state.translated_text,
                        lang_code=tts_code,
                    )
                    st.audio(audio_bytes, format="audio/mp3")
                except ValueError:
                    st.error("Text-to-speech is unavailable for this language.")
                except Exception:
                    st.error("Could not generate audio right now. Please try again.")


if __name__ == "__main__":
    main()
