import streamlit as st
import json
from services.whisper_service import WhisperService
from services.report_processor import ReportProcessor
from services.gpt_service import GPTService
from services.document_generator import DocumentGenerator
from questions_adviesrapport import ADVIESRAPPORT_QUESTIONS
from questions_analyserapport import ANALYSERAPPORT_QUESTIONS
from streamlit_mic_recorder import mic_recorder
from docx import Document
from io import BytesIO

def main():
    # Page config
    st.set_page_config(page_title="Pension Report Generator", layout="wide")
    st.title('Pension Benchmark Report Creator')
    st.write("Welkom bij de rapportopbouwtool voor de Benchmark Team. Alle input en output is in het Nederlands.")

    # Initialize services
    whisper_service = WhisperService(st.secrets["api_key"])
    gpt_service = GPTService(st.secrets["api_key"])
    report_processor = ReportProcessor(gpt_service)
    doc_generator = DocumentGenerator()

    # Audio Recording Section
    st.header("Neem uw adviesnotities op")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Optie 1: Neem direct op")
        audio_recorded = mic_recorder(
            start_prompt="Start Opname",
            stop_prompt="Stop Opname",
            key="recorder"
        )
        
    with col2:
        st.write("Optie 2: Upload een bestand")
        audio_file = st.file_uploader(
            "Upload een audio bestand",
            type=["wav", "mp3", "m4a"],
            key="file_uploader"
        )

    # Process audio input
    audio_input = None
    if audio_recorded:
        st.audio(audio_recorded['bytes'])
        st.success("Audio succesvol opgenomen!")
        audio_input = audio_recorded['bytes']
    elif audio_file:
        audio_input = audio_file

    if audio_input:
        # Transcription section
        if st.button("Transcribeer Audio"):
            with st.spinner("Bezig met transcriberen..."):
                transcript = whisper_service.transcribe_audio(audio_input)
                st.session_state['transcript'] = transcript
                st.success("Transcriptie voltooid!")
                
                with st.expander("Bekijk Transcriptie"):
                    st.text_area(
                        "Volledige transcriptie:",
                        value=transcript,
                        height=300
                    )

        # Report Generation section
        if 'transcript' in st.session_state and st.button("Genereer Rapporten"):
            with st.spinner("Bezig met rapporten genereren..."):
                try:
                    # Generate both reports
                    reports = report_processor.process_audio_to_reports(
                        st.session_state['transcript']
                    )

                    # Display reports in tabs
                    tab1, tab2 = st.tabs(["Adviesrapport", "Analyserapport"])
                    
                    with tab1:
                        st.markdown("### Adviesrapport")
                        st.markdown(reports["advice_report"])
                        
                        # Create Word document for advice report
                        advice_doc = doc_generator.create_report(
                            report_type="advice",
                            content=reports["advice_report"],
                            company_name=reports.get("company_name", ""),
                            date=reports.get("date", ""),
                            advisor_name=reports.get("advisor_name", "")
                        )
                        
                        # Save to BytesIO for download
                        docx_buffer = BytesIO()
                        advice_doc.save(docx_buffer)
                        docx_buffer.seek(0)
                        
                        if st.download_button(
                            "Download Adviesrapport (Word)",
                            docx_buffer,
                            file_name="adviesrapport.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        ):
                            st.success("Adviesrapport gedownload!")

                    with tab2:
                        st.markdown("### Analyserapport")
                        st.markdown(reports["analysis_report"])
                        
                        # Create Word document for analysis report
                        analysis_doc = doc_generator.create_report(
                            report_type="analysis",
                            content=reports["analysis_report"],
                            company_name=reports.get("company_name", ""),
                            date=reports.get("date", ""),
                            advisor_name=reports.get("advisor_name", "")
                        )
                        
                        # Save to BytesIO for download
                        docx_buffer = BytesIO()
                        analysis_doc.save(docx_buffer)
                        docx_buffer.seek(0)
                        
                        if st.download_button(
                            "Download Analyserapport (Word)",
                            docx_buffer,
                            file_name="analyserapport.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        ):
                            st.success("Analyserapport gedownload!")

                except Exception as e:
                    st.error(f"Er is een fout opgetreden: {str(e)}")
                    st.write("Details van de fout:")
                    st.write(e)

    # Display helpful information
    with st.expander("Help & Informatie"):
        st.write("""
        ### Hoe gebruikt u deze tool:
        1. Neem audio op of upload een audiobestand
        2. Klik op 'Transcribeer Audio' om de tekst te genereren
        3. Controleer de transcriptie
        4. Klik op 'Genereer Rapporten' om beide rapporttypes te maken
        5. Download de gewenste rapporten als Word-document
        """)

if __name__ == "__main__":
    main()