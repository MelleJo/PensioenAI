from questions_adviesrapport import ADVIESRAPPORT_QUESTIONS
from questions_analyserapport import ANALYSERAPPORT_QUESTIONS
from templates.advice_template import ADVICE_REPORT_TEMPLATE
import json

class ReportProcessor:
    def __init__(self, openai_client):
        self.client = openai_client
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
            # First, extract answers for both report types
            advice_answers = self._extract_answers(transcript, "advice")
            analysis_answers = self._extract_answers(transcript, "analysis")
            
            # Generate both reports using GPT-4o
            advice_report = self._generate_report("advice", advice_answers)
            analysis_report = self._generate_report("analysis", analysis_answers)
            
            return {
                "advice_report": advice_report,
                "analysis_report": analysis_report
            }
        except Exception as e:
            raise Exception(f"Error processing reports: {str(e)}")
    
    def _extract_answers(self, transcript, report_type):
        """Extract relevant answers from transcript based on report type"""
        try:
            questions = ADVIESRAPPORT_QUESTIONS if report_type == "advice" else ANALYSERAPPORT_QUESTIONS
            
            prompt = f"""
            Hier is een audio transcript van een gesprek over een pensioenadvies.
            Extraheer de antwoorden op de volgende vragen uit de transcriptie.
            Geef alleen de antwoorden, geen extra tekst.
            
            Transcript:
            {transcript}
            
            Vragen:
            {json.dumps(questions, indent=2)}
            
            Antwoord in het volgende format:
            {{
                "vraag1": "antwoord1",
                "vraag2": "antwoord2",
                ...
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            return self._parse_answers(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Error extracting answers: {str(e)}")
    
    def _parse_answers(self, gpt_response):
        """Parse the GPT response into a structured format"""
        try:
            # Try to parse as JSON first
            try:
                return json.loads(gpt_response)
            except json.JSONDecodeError:
                # If not JSON, try to parse line by line
                answers = {}
                lines = gpt_response.split('\n')
                current_question = None
                current_answer = []
                
                for line in lines:
                    line = line.strip()
                    if line in ADVIESRAPPORT_QUESTIONS or line in ANALYSERAPPORT_QUESTIONS:
                        if current_question:
                            answers[current_question] = ' '.join(current_answer).strip()
                        current_question = line
                        current_answer = []
                    elif line and current_question:
                        current_answer.append(line)
                
                if current_question and current_answer:
                    answers[current_question] = ' '.join(current_answer).strip()
                
                return answers
        except Exception as e:
            raise Exception(f"Error parsing answers: {str(e)}")
    
    def _generate_report(self, report_type, answers):
        """Generate report content using GPT-4o"""
        try:
            template = ADVICE_REPORT_TEMPLATE if report_type == "advice" else self.ANALYSIS_TEMPLATE
            
            prompt = f"""
            Genereer een pensioenrapport op basis van deze template en antwoorden.
            Behoud exact dezelfde formatting als de template.
            Vervang alleen de variabelen met de juiste inhoud.
            
            Template:
            {template}
            
            Antwoorden:
            {json.dumps(answers, indent=2, ensure_ascii=False)}
            
            Genereer het volledige rapport waarbij alle placeholders zijn vervangen met de juiste inhoud.
            Behoud alle opmaak, kopjes, en structuur van de template.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating report: {str(e)}")