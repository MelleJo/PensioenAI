import openai

class GPTService:
    def __init__(self, api_key):
        openai.api_key = api_key

    def generate_report_text(self, question_answers):
        """
        Function to use GPT-4-O API to generate report text based on answers.
        """
        prompt = "Construct a report based on the following input: "
        for question, answer in question_answers.items():
            prompt += f"\n{question}: {answer}"

        response = openai.Completion.create(
            engine="gpt-4-o",
            prompt=prompt,
            max_tokens=500
        )
        return response.choices[0].text.strip()
