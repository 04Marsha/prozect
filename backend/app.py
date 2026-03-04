from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import T5Tokenizer, T5ForConditionalGeneration

app = Flask(__name__)
CORS(app)

# Load T5 model and tokenizer
MODEL_NAME = "t5-small"
tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME, legacy=False)
model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)

def fetch_transcript(video_id: str) -> str:
    try:
        api = YouTubeTranscriptApi()
        
        transcript_list = api.list(video_id)
        
        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            transcript = next(iter(transcript_list))
        
        data = transcript.fetch()
        
        return " ".join(item.text for item in data)
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def transcript_summarizer(text: str) -> str:
    if not text:
        return "No text available."
    
    input_text = "summarize: " + text
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=1024, truncation=True)
    
    outputs = model.generate(
        inputs, 
        max_length=150, 
        min_length=40, 
        length_penalty=2.0, 
        num_beams=4, 
        early_stopping=True
    )
    
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

@app.route("/api/summarize", methods=["POST"])
def summarize_api():
    data = request.get_json(silent=True)
    if not data or "videoId" not in data:
        return jsonify({"error": "videoId is required"}), 400

    video_id = data.get("videoId")
    
    transcript_text = fetch_transcript(video_id)
    if not transcript_text:
        return jsonify({"error": "Could not retrieve transcript for this video."}), 404

    try:
        summary = transcript_summarizer(transcript_text)
        return jsonify({
            "videoId": video_id,
            "summary": summary
        })
    except Exception as e:
        return jsonify({"error": "Summarization failed", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)