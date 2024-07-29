from flask import Flask, request
import os, json

f = open("manifest.json", "r")
manifest = json.loads(f.read())
f.close()
current = manifest.get("current", 0)

app = Flask(__name__)




@app.route("/get_directive/<int:size>")
def get_directive(size):
    global current
    current += size
    return json.dumps([current-size, current])
@app.route("/submit/<int:start>/<int:end>", methods = ["POST"])
def submit(start, end):
    fname = f"{start}-{end}.bin"
    path = os.path.join("data", fname)
    while os.path.exists(path):
        path += ".rep"
    f = open(path, "wb")
    f.write(request.get_data())
    f.close()

    return "Submited"

if __name__ ==  "__main__":
    try:
        app.run()
    finally:
        manifest["current"] = current
        f = open("manifest.json", "w")
        f.write(json.dumps(manifest))
        f.close()