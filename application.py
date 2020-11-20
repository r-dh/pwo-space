import os


from flask import Flask, request, render_template, Response, jsonify
from chatbot.masterbot import MasterBot 
from audio.texttohash import TextToHash

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
masterbot = MasterBot()
hash_ = TextToHash()

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/wav")
def streamwav():
    def generate():
        with open("audio/out150.wav", "rb") as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)
    return Response(generate(), mimetype="audio/x-wav")

@app.route('/process', methods=['POST'])
def get_bot_response():
    print("[SPACEAPP] /process received POST request in backend:\n\t- Request form:", request.form)

    user_input = request.form.get("user_input", False) #request.form["user_input"]

    if not user_input:
    	form = request.get_json()
    	user_input = form["user_input"]

    if not user_input.strip():
        return jsonify({"bot_response" : "Sorry, ik begrijp je niet."})

    category, response = masterbot.answer(user_input.strip())
    response_hash = hash_.hash(response)
    print(f"[DEBUG] Hash: {response_hash}")
    print(f"[DEBUG] File exists: " + str(os.path.isfile(f"./audio/output/{response_hash}.wav")))

    if os.path.isfile(f"./audio/output/{response_hash}.wav"):
    	def generate(responsehash):
    	    with open(f"{os.getcwd()}/audio/output/{responsehash}.wav", "rb") as fwav:
    	        data = fwav.read(1024)
    	        while data:
    	            yield data
    	            data = fwav.read(1024)
    	return Response(generate(response_hash), mimetype="audio/x-wav")

    print("[SPACEAPP] Detected category: ",category)
    print("[SPACEAPP] Response:", response, "\n")
    dictResponse = jsonify({ 'bot_response': response })

    return dictResponse #response


if __name__ == "__main__":
    app.run(debug=True)