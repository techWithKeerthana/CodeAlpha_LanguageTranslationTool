"""Streamlit UI for the CodeAlpha Language Translation Tool."""

from __future__ import annotations

from io import BytesIO

import pyperclip
import streamlit as st
from gtts import gTTS

from translator import get_supported_languages, translate_text


def text_to_speech_audio(text: str, lang_code: str) -> bytes:
    """Convert text to speech and return MP3 bytes."""
    buffer = BytesIO()
    tts = gTTS(text=text, lang=lang_code)
    tts.write_to_fp(buffer)
    return buffer.getvalue()


def main() -> None:
    st.set_page_config(page_title="Language Translation Tool", page_icon="🌐")
    st.title("Language Translation Tool")
    st.caption("CodeAlpha AI Internship - Task 1")

    st.write("Enter text, choose languages, and click Translate.")

    languages = get_supported_languages()
    source_options = {"Auto Detect": "auto", **languages}
    target_options = languages

    input_text = st.text_area("Enter text", height=150, placeholder="Type text here...")

    col1, col2 = st.columns(2)
    with col1:
        source_label = st.selectbox("Source language", list(source_options.keys()), index=0)
    with col2:
        target_label = st.selectbox("Target language", list(target_options.keys()), index=26)

    if "translated_text" not in st.session_state:
        st.session_state.translated_text = ""

    if "target_code" not in st.session_state:
        st.session_state.target_code = "en"

    if st.button("Translate", type="primary"):
        source_code = source_options[source_label]
        target_code = target_options[target_label]

        try:
            st.session_state.translated_text = translate_text(
                text=input_text,
                source_lang=source_code,
                target_lang=target_code,
            )
            st.session_state.target_code = target_code
            st.success("Translation complete.")
        except ValueError as exc:
            st.error(str(exc))
        except RuntimeError as exc:
            st.error(str(exc))

    if st.session_state.translated_text:
        st.subheader("Translated text")
        st.text_area("Output", st.session_state.translated_text, height=150, disabled=True)

        action_col1, action_col2 = st.columns(2)

        with action_col1:
            if st.button("Copy to Clipboard"):
                try:
                    pyperclip.copy(st.session_state.translated_text)
                    st.success("Copied translated text to clipboard.")
                except pyperclip.PyperclipException:
                    st.error("Clipboard is not available on this system.")

        with action_col2:
            if st.button("Listen"):
                try:
                    audio_bytes = text_to_speech_audio(
                        text=st.session_state.translated_text,
                        lang_code=st.session_state.target_code,
                    )
                    st.audio(audio_bytes, format="audio/mp3")
                except ValueError:
                    st.error("Text-to-speech is unavailable for this language.")
                except Exception:
                    st.error("Could not generate audio right now. Please try again.")


if __name__ == "__main__":
    main()
