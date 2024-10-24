import streamlit as st
import json
from whisper_service import WhisperService
from gpt_service import GPTService
from report_service import ReportService
from questions_adviesrapport import ADVIESRAPPORT_QUESTIONS
from questions_analyserapport import ANALYSERAPPORT_QUESTIONS
from advies_template import ADVICE_REPORT_TEMPLATE
from streamlit_mic_recorder import mic_recorder
# from checklist_component import display_checklist

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Main App Functionality
def main():
    # Initialize services
    whisper_service = WhisperService(st.secrets["api_key"])
    gpt_service = GPTService(st.secrets["api_key"])
    report_service = ReportService(whisper_service, gpt_service)

    # Set up the page
    st.title('Pension Benchmark Report Creator')
    st.write("Welkom bij de rapportopbouwtool voor de Benchmark Team. Alle input en output is in het Nederlands.")

    # Audio Recording Section
    st.header("Neem uw adviesnotities op")
    # display_checklist()
    st.write("Klik op de microfoonknop om de opname te starten. Klik nogmaals om te stoppen.")
    audio_recorded = mic_recorder(start_prompt="Start Opname", stop_prompt="Stop Opname", key="recorder")

    if audio_recorded:
        st.audio(audio_recorded['bytes'])
        st.success("Audio succesvol opgenomen!")
        audio_input = audio_recorded['bytes']
    else:
        # User input: Single audio file for the entire process
        st.header("Upload een geluidsbestand voor de gehele rapportage")
        audio_input = st.file_uploader("Upload een audio bestand", type=config["allowedAudioTypes"], key="full_audio")

    question_answers = {}

    if audio_input is not None:
        st.write("Bezig met transcriberen...")
        transcript = whisper_service.transcribe_audio(audio_input)
        st.write("Transcript voltooid!")
        st.text_area("Volledige transcriptie:", value=transcript, height=300)

        # Splitting transcript into sections for each question
        # Assuming each section is preceded by a known question or indicator (simplified splitting for demonstration purposes)
        transcript_sections = transcript.split("\n")  # Assuming each answer is on a new line
        for idx, question in enumerate(ADVIESRAPPORT_QUESTIONS + ANALYSERAPPORT_QUESTIONS):
            if idx < len(transcript_sections):
                question_answers[question] = transcript_sections[idx]
            else:
                question_answers[question] = ""

    # Report Generation
    if st.button("Genereer rapport"):
        if question_answers:
            with st.spinner('Bezig met rapport genereren...'):
                # Generate report by filling in the template
                report_text = ADVICE_REPORT_TEMPLATE.format(
                    bedrijf_naam=question_answers.get("Wat is de naam van het bedrijf?", ""),
                    datum_adviesrapportage=question_answers.get("Wat is de datum van de opmaak van de adviesrapportage?", ""),
                    adviseur_naam=question_answers.get("Wat is de naam van de adviseur?", ""),
                    huidige_pensioenuitvoerder=question_answers.get("Wat is naam van de huidige pensioenuitvoerder?", ""),
                    nieuwe_pensioenuitvoerder=question_answers.get("Wat is de naam van de nieuwe pensioenuitvoerder en waarom?", ""),
                )
                st.success("Rapport gegenereerd!")
                st.subheader("Gegenereerde rapporttekst")
                st.write(report_text)
        else:
            st.warning("Gelieve een audio bestand te uploaden en ervoor te zorgen dat alle vragen beantwoord zijn.")

    # Placeholder for structured report format
    st.header("Structuur van het rapport")
    st.write("Naam: [Naam hier]")
    st.write("Rapporttekst: [Hier komt de tekst gegenereerd door AI]")

if __name__ == "__main__":
    main()
