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

def display_questions():
    """Display questions in the exact format provided"""
    
    # Adviesrapport Questions
    st.markdown("### **1. Vragenlijst voor Adviesrapportage:**")
    
    advies_questions = """
    - **Vraag 1:** Wat is de naam van het bedrijf?
    
    - **Vraag 2:** Wat is de datum van de opmaak van de adviesrapportage?
    
    - **Vraag 3:** Wat is de naam van de adviseur?
    
    - **Vraag 4:** Is er gekozen voor een flat rate of voor een eerbiedigende werking? Wat is de aanleiding geweest van dit besluit?
    
    - **Vraag 5:** Geef een onderbouwing voor de keuze voor de hoogte van het percentage van het nabestaandenpensioen. Is dat het hoogste percentage uit de oude regeling, is dat het gemiddelde van de oude regeling of is dat marktconform?
    
    - **Vraag 6:** Is er een 'wat wil ik?' presentatie waar naar verwezen moet worden?
    
    - **Vraag 7:** Is er een gespreksverslag waar naar verwezen moet worden?
    
    - **Vraag 8:** Wat is naam van de huidige pensioenuitvoerder?
    
    - **Vraag 9:** Is de werkgever tevreden met de huidige pensioenuitvoerder of niet? En waarom is hij wellicht niet tevreden?
    
    - **Vraag 10:** Wat is de naam van de nieuwe pensioenuitvoerder en waarom?
    
    - **Vraag 11:** Wil de werkgever wel of geen deelnemerscommunicatie? Of doet de werkgever dit zelf? Of in nader overleg?
    """
    
    # Analyserapport Questions
    st.markdown(advies_questions)
    st.markdown("### **2. Vragenlijst voor Analyserapportage:**")
    
    analyse_questions = """
    - **Vraag 1:** Wat is de naam van het bedrijf?
    
    - **Vraag 2:** Wat is de datum van de opmaak van de adviesrapportage?
    
    - **Vraag 3:** Wat is de naam van de adviseur?
    
    - **Vraag 4:** Welke verplichtstellingen zijn er onderzocht? En wat zijn de uitkomsten van dit onderzoek?
    
    - **Vraag 5:** Wat is de uitkomst van het financiële onderzoek? Is dat een minder of een meer dan gemiddeld risico? En wanneer er een meer dan gemiddeld risico is, waarop is dat dan gebaseerd?
    """
    
    st.markdown(analyse_questions)

def process_audio(audio_data, whisper_service, gpt_service, report_processor, doc_generator):
    """Process audio data through the complete pipeline"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Transcription
        status_text.write("🎯 Bezig met transcriberen...")
        progress_bar.progress(20)
        transcript = whisper_service.transcribe_audio(audio_data)
        st.session_state['transcript'] = transcript
        
        # Show transcript in expander
        with st.expander("Transcriptie", expanded=False):
            st.text_area("Volledige transcriptie:", value=transcript, height=200)
        
        # Step 2: Generate Reports
        status_text.write("📝 Bezig met rapporten genereren...")
        progress_bar.progress(40)
        reports = report_processor.process_audio_to_reports(transcript)
        progress_bar.progress(60)
        
        # Step 3: Create Documents
        status_text.write("📄 Bezig met documenten opmaken...")
        progress_bar.progress(80)
        
        # Display reports in tabs
        tab1, tab2 = st.tabs(["Adviesrapport", "Analyserapport"])
        
        with tab1:
            st.markdown("### Adviesrapport")
            advice_doc = doc_generator.create_report(
                report_type="advice",
                content=reports["advice_report"],
                company_name=reports.get("company_name", ""),
                date=reports.get("date", ""),
                advisor_name=reports.get("advisor_name", "")
            )
            
            docx_buffer = BytesIO()
            advice_doc.save(docx_buffer)
            docx_buffer.seek(0)
            
            st.download_button(
                "⬇️ Download Adviesrapport (Word)",
                docx_buffer,
                file_name="adviesrapport.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        with tab2:
            st.markdown("### Analyserapport")
            analysis_doc = doc_generator.create_report(
                report_type="analysis",
                content=reports["analysis_report"],
                company_name=reports.get("company_name", ""),
                date=reports.get("date", ""),
                advisor_name=reports.get("advisor_name", "")
            )
            
            docx_buffer = BytesIO()
            analysis_doc.save(docx_buffer)
            docx_buffer.seek(0)
            
            st.download_button(
                "⬇️ Download Analyserapport (Word)",
                docx_buffer,
                file_name="analyserapport.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        
        progress_bar.progress(100)
        status_text.write("✅ Verwerking voltooid! Download de rapporten hieronder.")
        
    except Exception as e:
        progress_bar.progress(100)
        status_text.write("❌ Er is een fout opgetreden")
        st.error(f"Er is een fout opgetreden: {str(e)}")
        st.write("Details van de fout:")
        st.write(e)

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

    # Display questions guide
    display_questions()

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

    # Automatic processing when audio is available
    if audio_recorded:
        st.audio(audio_recorded['bytes'])
        st.success("Audio succesvol opgenomen!")
        process_audio(audio_recorded['bytes'], whisper_service, gpt_service, 
                     report_processor, doc_generator)
    elif audio_file:
        process_audio(audio_file, whisper_service, gpt_service, 
                     report_processor, doc_generator)

    # Help information
    with st.expander("Help & Informatie"):
        st.write("""
        ### Hoe gebruikt u deze tool:
        1. Bekijk de vragen die beantwoord moeten worden
        2. Neem audio op of upload een audiobestand
        3. Wacht tot de verwerking voltooid is
        4. Download de gegenereerde rapporten
        """)

if __name__ == "__main__":
    main()