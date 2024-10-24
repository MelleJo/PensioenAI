import streamlit as st
from whisper_service import WhisperService
from gpt_service import GPTService
from report_service import ReportService
from questions_adviesrapport import ADVIESRAPPORT_QUESTIONS
from questions_analyserapport import ANALYSERAPPORT_QUESTIONS
from advies_template import ADVICE_REPORT_TEMPLATE

# Main App Functionality
def main():
    # Initialize services using a single API key for both Whisper and GPT
    api_key = st.secrets["api_key"]  # Unified API key for both services
    whisper_service = WhisperService(api_key)
    gpt_service = GPTService(api_key)
    report_service = ReportService(whisper_service, gpt_service)

    # Set up the page
    st.title('Pension Benchmark Report Creator')
    st.write("Welkom bij de rapportopbouwtool voor de Benchmark Team. Alle input en output is in het Nederlands.")

    # User inputs
    st.header("Vragen voor de pensioen maniwaker")
    questions = ADVIESRAPPORT_QUESTIONS + ANALYSERAPPORT_QUESTIONS
    question_answers = {}
    audio_inputs = []

    # Loop through questions and transcribe answers
    for question in questions:
        st.write(question)
        audio_input = st.file_uploader(f"Upload antwoord op de vraag '{question}' (audio bestand in .wav format)", type=["wav"], key=question)
        if audio_input is not None:
            st.write("Bezig met transcriberen...")
            transcript = whisper_service.transcribe_audio(audio_input)
            st.write("Transcript: " + transcript)
            question_answers[question] = transcript
            audio_inputs.append(audio_input)

    # Report Generation
    if st.button("Genereer rapport"):
        if len(question_answers) == len(questions):
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
            st.warning("Gelieve een antwoord op elke vraag te uploaden.")

    # Placeholder for structured report format
    st.header("Structuur van het rapport")
    st.write("Naam: [Naam hier]")
    st.write("Rapporttekst: [Hier komt de tekst gegenereerd door AI]")

if __name__ == "__main__":
    main()
