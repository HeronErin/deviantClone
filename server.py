from flask import Flask, request
import os, json, time

f = open("manifest.json", "r")
manifest = json.loads(f.read())
manifest["ipDict"] = manifest.get("ipDict", {})
f.close()
current = manifest.get("current", 0)


def saveManifest():
    global manifest
    global current

    manifest["current"] = current
    f = open("manifest.json", "w")
    f.write(json.dumps(manifest, indent = 4))
    f.close()

app = Flask(__name__)


@app.route("/get_directive/<int:size>")
def get_directive(size):
    global current
    current += size
    manifest["ipDict"][request.remote_addr] = time.ctime()
    saveManifest()
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
        app.run(host = "0.0.0.0", port = 80)
    finally:
        saveManifest()
