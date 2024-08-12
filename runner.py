import oembed, requests, gzip, time, traceback


server = "http://127.0.0.1:1234/"
size = 100
threads = 1

threadList = []

runningFor = time.time()
completed = 0

waitingForExit = False

if __name__ == "__main__":
	ses = requests.session()
	while True:
		tl2 = threadList
		results = [t for t in tl2 if not t[0].is_alive()]
		threadList = [t for t in tl2 if t[0].is_alive()]

		while len(threadList) < threads and not waitingForExit:
			while True:
				try:
					r = ses.get(server + "/get_directive/")
					break
				except Exception as e: print(traceback.format_exc())
			urlList = r.json()
			start = urlList.pop(0)
			print(start, len(urlList))
			t = oembed.Getter(start, size, urlList)
			t.start()
			threadList.append([t, start, start + size])


		for r in results:
			completed += size
			while True:
				try: 
					ses.post(server + "/submit/" + str(r[1]) + "/" + str(r[2]), data=gzip.compress(r[0].bakeResults()))
					break
				except Exception as e: print(traceback.format_exc())

		if len(results):
			diff = time.time() - runningFor
			print("Completed", completed, "in", diff, "secounds. Or", completed / diff, "per secound.")
		elif waitingForExit and len(threadList) == 0:
			exit(0)
		else:
			try:
				time.sleep(0.5)
			except KeyboardInterrupt:
				waitingForExit = True
				print("Waiting for threads to complete")


