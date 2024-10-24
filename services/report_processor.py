class ReportProcessor:
    def __init__(self, openai_client):
        self.client = openai_client
        
    def process_audio_to_reports(self, transcript):
        """Generate both advice and analysis reports from a single audio transcript"""
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
    
    def _extract_answers(self, transcript, report_type):
        """Extract relevant answers from transcript based on report type"""
        prompt = f"""
        Given the following transcript, extract answers for the {report_type} report questions:
        
        Transcript: {transcript}
        
        Questions to answer:
        {ADVIESRAPPORT_QUESTIONS if report_type == "advice" else ANALYSERAPPORT_QUESTIONS}
        
        Provide answers in a structured format.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        return self._parse_answers(response.choices[0].message.content)
    
    def _generate_report(self, report_type, answers):
        """Generate report content using GPT-4o"""
        template = ADVICE_TEMPLATE if report_type == "advice" else ANALYSIS_TEMPLATE
        
        prompt = f"""
        Generate a pension report based on the following template and answers.
        Keep all formatting and structure identical to the template.
        
        Template:
        {template}
        
        Answers:
        {answers}
        
        Generate the complete report with all placeholders replaced with appropriate content.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        return response.choices[0].message.content