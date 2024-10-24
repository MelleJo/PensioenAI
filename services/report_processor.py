from questions_adviesrapport import ADVIESRAPPORT_QUESTIONS
from questions_analyserapport import ANALYSERAPPORT_QUESTIONS
from templates.advice_template import ADVICE_REPORT_TEMPLATE

class ReportProcessor:
    def __init__(self, gpt_service):
        self.gpt_service = gpt_service
        self.ANALYSIS_TEMPLATE = """
Inventarisatie overstap naar de Wet Toekomst Pensioenen

Werkgever: {bedrijf_naam}

Analyserapportage
Datum: {datum_adviesrapportage}
Naam adviseur: {adviseur_naam}

Veldhuis Advies / JIP Financieel

Samenvatting
Tijdens onze eerdere gesprekken hebben wij geïnventariseerd wat uw wensen en doelstellingen zijn.
[Rest van template hier...]
"""
        
    def process_audio_to_reports(self, transcript):
        """Generate both advice and analysis reports from a single audio transcript"""
        try:
            # Extract answers for both report types
            advice_answers = self.gpt_service.extract_answers(
                transcript, 
                ADVIESRAPPORT_QUESTIONS
            )
            analysis_answers = self.gpt_service.extract_answers(
                transcript, 
                ANALYSERAPPORT_QUESTIONS
            )
            
            # Generate both reports
            advice_report = self.gpt_service.generate_report_text({
                'template': ADVICE_REPORT_TEMPLATE,
                'answers': advice_answers
            })
            analysis_report = self.gpt_service.generate_report_text({
                'template': self.ANALYSIS_TEMPLATE,
                'answers': analysis_answers
            })
            
            return {
                "advice_report": advice_report,
                "analysis_report": analysis_report
            }
        except Exception as e:
            raise Exception(f"Error processing reports: {str(e)}")