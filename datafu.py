import sys, os, gzip, oembed, json
def join():
	startToFile = {int(f.split("-")[0]):f for f in os.listdir("data") if f.endswith(".bin")}

	for key in sorted(startToFile.keys()):
		if not key in startToFile:
			continue
		name = startToFile[key]
		if os.stat(os.path.join("data", name)) > 20*1024*1024:
			continue
		end = int(name.split("-")[1].split(".")[0])
		
		while end in startToFile:
			f = open(os.path.join("data", name), "rb")
			p1 = gzip.decompress(f.read())
			f.close()

			f = open(os.path.join("data", startToFile[end]), "rb")
			p2 = gzip.decompress(f.read())
			f.close()

			newBin = gzip.compress(p1 + p2)

			end2 = startToFile[end].split("-")[1]
			newName = name.split("-")[0] + "-" + end2
			
			os.remove(os.path.join("data", startToFile[end]))
			os.rename(os.path.join("data", name), os.path.join("data", newName))

			f = open(os.path.join("data", newName), "wb")
			f.write(newBin)
			f.close()

			name = newName
			del startToFile[end]
			end = int(end2.split(".")[0])
def ext(path, index=None):
	f = open(path, "rb")
	res = oembed.bulkDecode(gzip.decompress(f.read()))
	f.close()
	if index is not None:
		res = res[index]
	json.dump(res, sys.stdout, indent=4)
	sys.stdout.write("\n")


		

if __name__ == "__main__":
	if len(sys.argv) == 1:
		print("Please use one of the valid arguments: join")
		exit(1)
	if sys.argv[1] == "join":
		join()
	elif sys.argv[1] == "ext":
		if len(sys.argv) == 2:
			print("Please provide a file to extract.")
		elif len(sys.argv) == 3:
			ext(sys.argv[2])
		else:
			ext(sys.argv[2], int(sys.argv[3]))