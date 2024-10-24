from openai import OpenAI

class GPTService:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def generate_report_text(self, question_answers):
        """
        Function to use GPT-4-O API to generate report text based on answers.
        """
        prompt = "Construct a report based on the following input: "
        for question, answer in question_answers.items():
            prompt += f"\n{question}: {answer}"

        response = self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a professional pension advisor assistant that writes formal reports in Dutch."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        return response.choices[0].message.content

    def extract_answers(self, transcript, questions):
        """
        Function to extract answers from transcript for given questions.
        """
        prompt = f"""
        Analyze this transcript and extract answers for the following questions.
        Provide only the answers, no additional commentary.
        
        Transcript:
        {transcript}
        
        Questions:
        {questions}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts specific answers from transcripts accurately."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        return response.choices[0].message.content