import streamlit as st
import json
from services.whisper_service import WhisperService
from questions_adviesrapport import ADVIESRAPPORT_QUESTIONS
from questions_analyserapport import ANALYSERAPPORT_QUESTIONS
from docx import Document
from streamlit_mic_recorder import mic_recorder

# Main App Functionality
def main():
    # Initialize services
    whisper_service = WhisperService(st.secrets["api_key"])

    # Set up the page
    st.title('Pension Benchmark Report Creator')
    st.write("Welkom bij de rapportopbouwtool voor de Benchmark Team. Alle input en output is in het Nederlands.")

    # Audio Recording Section
    st.header("Neem uw adviesnotities op")
    st.write("Klik op de microfoonknop om de opname te starten. Klik nogmaals om te stoppen.")
    audio_recorded = mic_recorder(start_prompt="Start Opname", stop_prompt="Stop Opname", key="recorder")

    if audio_recorded:
        st.audio(audio_recorded['bytes'])
        st.success("Audio succesvol opgenomen!")
        audio_input = audio_recorded['bytes']
    else:
        # User input: Single audio file for the entire process
        st.header("Upload een geluidsbestand voor de gehele rapportage")
        audio_input = st.file_uploader("Upload een audio bestand", type=["wav", "mp3", "m4a"], key="full_audio")

    question_answers = {}

    if audio_input is not None:
        st.write("Bezig met transcriberen...")
        transcript = whisper_service.transcribe_audio(audio_input)
        st.write("Transcript voltooid!")
        st.text_area("Volledige transcriptie:", value=transcript, height=300)

        # Split the transcript into parts based on known questions
        # For simplicity, assume each section is separated by a period or new line
        transcript_sections = transcript.split(".")  # Assuming each answer ends with a period
        for idx, question in enumerate(ADVIESRAPPORT_QUESTIONS + ANALYSERAPPORT_QUESTIONS):
            if idx < len(transcript_sections):
                question_answers[question] = transcript_sections[idx].strip()
            else:
                question_answers[question] = ""

    # Report Generation
    if st.button("Genereer rapport"):
        if question_answers:
            with st.spinner('Bezig met rapport genereren...'):
                # Load the advice template from the provided docx file
                try:
                    document = Document("/mnt/data/Output Advies eerbiedigende werking.docx")
                    report_text = ""
                    for para in document.paragraphs:
                        report_text += para.text + "\n"

                    # Replace placeholders in the template with answers
                    report_text = report_text.replace("Werkgever X", question_answers.get("Wat is de naam van het bedrijf?", ""))
                    report_text = report_text.replace("24-05-2024", question_answers.get("Wat is de datum van de opmaak van de adviesrapportage?", ""))
                    report_text = report_text.replace("Thom Dijkstra", question_answers.get("Wat is de naam van de adviseur?", ""))
                    report_text = report_text.replace("Scildon", question_answers.get("Wat is naam van de huidige pensioenuitvoerder?", ""))
                    report_text = report_text.replace("Zwitserleven", question_answers.get("Wat is de naam van de nieuwe pensioenuitvoerder en waarom?", ""))

                    st.success("Rapport gegenereerd!")
                    st.subheader("Gegenereerde rapporttekst")
                    st.write(report_text)
                except Exception as e:
                    st.error(f"Er is een fout opgetreden bij het laden van de rapport template: {str(e)}")
        else:
            st.warning("Gelieve een audio bestand te uploaden en ervoor te zorgen dat alle vragen beantwoord zijn.")

    # Placeholder for structured report format
    st.header("Structuur van het rapport")
    st.write("Naam: [Naam hier]")
    st.write("Rapporttekst: [Hier komt de tekst gegenereerd door AI]")

if __name__ == "__main__":
    main()
