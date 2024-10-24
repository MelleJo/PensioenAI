import requests

class WhisperService:
    def __init__(self, api_key):
        self.api_key = api_key

    def transcribe_audio(self, audio_file):
        """
        Function to use Whisper API to transcribe audio to text.
        """
        # Determine content type based on file extension
        content_type = f'audio/{audio_file.name.split(".")[-1]}'
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': content_type
        }
        response = requests.post("https://api.whisper.com/v1/transcribe", headers=headers, data=audio_file.read())
        if response.status_code == 200:
            return response.json().get("text", "")
        else:
            return "Error transcribing audio."
