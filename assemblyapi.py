import requests
import json
import time
from get_credentials import get_assembyai_api
import os


# given the voice recording in output.wav, generates the transcript and summary
def get_transcript():
  base_url = "https://api.assemblyai.com/v2"

  # get API key from config file
  token = get_assembyai_api()

  headers = {
      "authorization": token
  }

  # opening recorded audio file
  file_path = os.path.join(os.path.dirname(__file__), "output.wav")
  with open(file_path, "rb") as f:
    response = requests.post(base_url + "/upload",
                            headers = headers,
                            data = f)

  upload_url = response.json()["upload_url"]

  data = {
      "audio_url": upload_url,
      "summarization": True,
      "speaker_labels": True,
      "summary_model": "informative",
      "summary_type": "bullets"
  }

  url = base_url + "/transcript"
  response = requests.post(url, json=data, headers=headers)

  transcript_id = response.json()['id']
  polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"

  while True:

    # get transcription result 
    transcription_result = requests.get(polling_endpoint, headers=headers).json()

    if transcription_result['status'] == 'completed':
      summary = transcription_result.get('summary', '')
      print("Transcription completed!")
      transcript_text = ""
      if "utterances" in transcription_result:
        for utt in transcription_result["utterances"]:
          speaker = utt["speaker"]
          text = utt["text"]
          transcript_text += f"{speaker}: {text}\n"
      else:
        transcript_text = transcription_result.get("text", "")
      # storing trancsription and summary in a dictionary and returning
      with open("output_transcript.txt", "w", encoding="utf-8") as f:
            f.write("Transcript\n")
            f.write(transcript_text)
            f.write("\nSummary \n")
            f.write(summary)
      print("[INFO] Transcript saved as output_transcript.txt")
      return transcription_result

    elif transcription_result['status'] == 'error':
      print("Transcription failed")

    else:
      time.sleep(3)
