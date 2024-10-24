class ReportService:
    def __init__(self, whisper_service, gpt_service):
        self.whisper_service = whisper_service
        self.gpt_service = gpt_service

    def transcribe_and_generate_report(self, questions, audio_inputs):
        question_answers = {}
        for question, audio_input in zip(questions, audio_inputs):
            transcript = self.whisper_service.transcribe_audio(audio_input)
            question_answers[question] = transcript
        return self.gpt_service.generate_report_text(question_answers)
