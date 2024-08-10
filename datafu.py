import sys, os, gzip, oembed, json, time, threading
import shutil
from concurrent.futures import ThreadPoolExecutor

JOUT = "out"
def join():
	startToFile = {int(f.split("-")[0]):f for f in os.listdir("data") if f.endswith(".bin")}

	for key in sorted(startToFile.keys()):
		if not key in startToFile:
			continue
		name = startToFile[key]

		end = int(name.split("-")[1].split(".")[0])

		print("-", os.path.join("data", name))
		f = open(os.path.join("data", name), "rb")
		p1 = gzip.decompress(f.read())
		f.close()

		gf = gzip.open("out.bin", "wb")
		gf.write(p1)
		end2 = name.split("-")[1]
		dels = []
		while end in startToFile:
			print("Fusing", startToFile[end])
			f = open(os.path.join("data", startToFile[end]), "rb")
			p2 = gzip.decompress(f.read())
			f.close()

			gf.write(p2)

			end2 = startToFile[end].split("-")[1]
			
			dels.append(os.path.join("data", startToFile[end]))
			

			del startToFile[end]
			end = int(end2.split(".")[0])


		gf.close()

		newName = name.split("-")[0] + "-" + end2

		xnew = str(time.time()) + ".bin"
		os.rename("out.bin", xnew)
		threading.Thread(target = shutil.move, args=(xnew, os.path.join(JOUT, newName))).start()
		
		os.remove(os.path.join("data", name))
		print("Removing", os.path.join("data", name))

		with ThreadPoolExecutor(max_workers=64) as exe:
			for d in dels:
				print("Removing", d)
				exe.submit(os.remove, d)
def ext(path, index=None):
	f = open(path, "rb")
	res = oembed.bulkDecode(gzip.decompress(f.read()))
	f.close()
	if index is not None:
		res = res[index]
	json.dump(res, sys.stdout, indent=4)
	sys.stdout.write("\n")
def getOld():
	jso = json.load(open("manifest.json", "r"))
	print(json.dumps(list(sorted(list(jso.get("ipDict", {}).items()), key=lambda x: x[1])), indent=4))
def fix(path):
	issues = [f for f in os.listdir(path) if f.split("-")[0] == f.split("-")[1].split(".")[0]]
	for ipath in issues:
		f = open(os.path.join(path, ipath), "rb")
		res = oembed.bulkDecode(gzip.decompress(f.read()))
		f.close()
		print(ipath)
		for i, v in enumerate(res):
			(id, _) = v
			if id != -1:
				os.rename(os.path.join(path, ipath), os.path.join(path, str(i + id) + "-" +str(i + id + len(res)) + ".bin" ))
				break

def rename(path):
	f = open(path, "rb")
	res = oembed.bulkDecode(gzip.decompress(f.read()))
	f.close()
	for i, v in enumerate(res):
		(id, _) = v
		if id != -1:
			os.rename(path, str(i + id) + "-" +str(i + id + len(res)) + ".bin" )
			break
def jobs():
	files = [(int(d.split("-")[0]), int(d.split("-")[1].split(".")[0]), d) for d in os.listdir("data") if d.endswith(".bin")]
	files = list(sorted(files, key=lambda x: int(x[0])))
	genJobs = []
	for i, (start, end, fname) in enumerate(files):
		if i == len(files) -1:
			continue
		xdiff = int(files[i+1][0]) - int(end)

		if xdiff <= 0:
			continue

		start = int(end)
		

		while xdiff > 0:
			xstart = start
			diff = min(20_000, xdiff)
			xdiff -= diff
			
			start += diff
			genJobs.append([xstart, start])
	print(json.dumps(genJobs, indent = 4))
def fill():
	maxThreads = 25
	threadList = []
	files = [(int(d.split("-")[0]), int(d.split("-")[1].split(".")[0]), d) for d in os.listdir("data") if d.endswith(".bin")]
	files = list(sorted(files, key=lambda x: int(x[0])))
	def handle(data):
		bin = str(data[1]) + "-" + str(data[2]) + ".bin"
		print(bin)
		f = open(os.path.join("data", bin), "wb" )
		f.write(gzip.compress(data[0].bakeResults()))
		f.close()
	for i, (start, end, fname) in enumerate(files):
		if i == len(files) -1:
			continue

		xdiff = int(files[i+1][0]) - int(end)

		if xdiff <= 0:
			continue

		start = int(end)
		jobs = []

		while xdiff > 0:
			xstart = start
			diff = min(20_000, xdiff)
			xdiff -= diff
			
			start += diff
			jobs.append((xstart, start))
		while len(jobs):
			while len(threadList) >= maxThreads:
				tl2 = threadList
				results = [handle(t) for t in tl2 if not t[0].is_alive()]
				threadList = [t for t in tl2 if t[0].is_alive()]

				if 0 != len(results):
					time.sleep(0.5)
			start, end = jobs.pop()
			t = oembed.Getter(start, end)
			t.start()
			print("Starting", start, "with xdiff", end-start)
			threadList.append([t, start, end])
	for t in threadList:
		t[0].join()
		handle(t)

		

if __name__ == "__main__":
	if len(sys.argv) == 1:
		print("Please use one of the valid arguments: join")
		exit(1)
	elif sys.argv[1] == "genJobs":
		jobs()
	elif sys.argv[1] == "join":
		join()
	elif sys.argv[1] == "old":
		getOld()
	elif sys.argv[1] == "fix":
		fix(sys.argv[2])
	elif sys.argv[1] == "rename":
		rename(sys.argv[2])
	elif sys.argv[1] == "ext":
		if len(sys.argv) == 2:
			print("Please provide a file to extract.")
		elif len(sys.argv) == 3:
			ext(sys.argv[2])
		else:
			ext(sys.argv[2], int(sys.argv[3]))
