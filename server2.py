from flask import Flask, request
import os, json, time, gzip
from datafu import SPLT

f = open("manifest.json", "r")
manifest = json.loads(f.read())
manifest["ipDict"] = manifest.get("ipDict", {})
f.close()
current = manifest.get("current", 0)


def getUrlRange(leng):
    stop = current + leng
    fs = current // SPLT
    fe = stop // SPLT
    data = []
    
    for num in range(fs, fe + 1):
        fn = os.path.join("real_links", f"{num}.SORT.txt.gz")
        print(fn, os.path.exists(fn))
        # if not os.path.exists(fn):
            # continue
        # print(fn)
        f = gzip.open(fn, "rb")
        
        data += filter(
            lambda x: current <= int(x.split(b"-")[-1]) < stop,
            f.readlines()
        )
        print(len(data))
        
        f.close()
    return list(map(
        lambda x: x.decode("ascii").strip(),
        data
    ))

def saveManifest():
    global manifest
    global current

    manifest["current"] = current
    f = open("manifest.json", "w")
    f.write(json.dumps(manifest, indent = 4))
    f.close()

app = Flask(__name__)
SZ = 100
print(getUrlRange(SZ))

@app.route("/get_directive/")
def get_directive():
    global current
    data = [current] + getUrlRange(SZ)
    print(len(data))
    current += SZ
    manifest["ipDict"][request.remote_addr] = time.ctime()
    saveManifest()
    return json.dumps(data)

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
        app.run(host = "0.0.0.0", port = 1234)
    finally:
        saveManifest()
