import oembed, requests, gzip, time, traceback


server = "http://10.128.0.5:5000"
size = 10_000
threads = 10

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
					r = ses.get(server + "/get_directive/" + str(size))
					break
				except Exception as e: traceback.print_exception(e)
			start, end = r.json()
			t = oembed.Getter(start, end)
			t.start()
			threadList.append([t, start, end])


		for r in results:
			completed += size
			while True:
				try: 
					ses.post(server + "/submit/" + str(r[1]) + "/" + str(r[2]), data=gzip.compress(r[0].bakeResults()))
					break
				except Exception as e: traceback.print_exception(e)

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


