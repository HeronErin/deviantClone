import requests, threading, time, json
import struct
import dateutil.parser
import datetime
import gzip
import traceback
import random

class Getter(threading.Thread):
	def __init__(self, start, xlen, urlList):
		self.startIndex = start
		self.xlen = xlen
		self.urlList = urlList
		threading.Thread.__init__(self)

		self.results = None
	def run(self):
		results = {}
		session = requests.session()
		for url in self.urlList:
			jsoFail = 0
			while 1:
				try:
					ver = f"{random.randrange(500, 540)}.{random.randrange(10, 40)}"
					h = {
						"User-Agent": f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{ver} (KHTML, like Gecko) Chrome/127.0.0.0 Safari/{ver}",
						'SEC-CH-UA': f'"Chrome";v="{random.randrange(100, 130)}", "Not)A;Brand";v="99"',
						'SEC-CH-UA-MOBILE': '?0',
						'Sec-CH-UA-Platform': "Windows"
						}

					r = session.get(
						f"https://backend.deviantart.com/oembed?url={url}",
						headers = h,
						timeout=15)
					print(r)
					if r.status_code == 200:
						try: 
							if jsoFail > 25:
								break
							
							json.loads(r.text)
						except json.decoder.JSONDecodeError:
							jsoFail += 1
							f = open("Not jsonable", "a")
							f.write(r.text + "\n")
							f.close()
							continue
					if r.status_code == 200 or r.status_code == 404:
						results[int(url.split("-")[-1])] = r.text
						break
					else:
						print(r)
						time.sleep(1)
				except Exception as e:
					print(traceback.format_exc())
					time.sleep(1)
		self.results = results
		print("Completed range", self.startIndex, "-",  self.xlen)

	def bakeResults(self):
		assert self.results is not None
		bdata = b""
		for i in range(self.startIndex, self.startIndex + self.xlen):
			if not i in self.results or self.results[i].startswith("404 Not Found"):
				bdata += b"\x00"
			else:
				bdata += serialize(i, json.loads(self.results[i]))
		return bdata


# Binary format:
# bool: is avalible. If null the rest will not be present.

# 5 ints network endian (unsigned)
# id, views, favs, comments, downloads

# 1 long (unsigned)
# Publish date

# 2 shorts (unsigned)
# width, height

# strings:
# title, type, author, url

# String format:
# ushort for size, followed by ascii data

def _deserializeString(data, offset):
    length = struct.unpack_from("!H", data, offset)[0]
    offset += 2
    string = data[offset:offset+length].decode("utf-8")
    offset += length
    return string, offset
def _serializeString(string):
	if string is None:
		string = "<NULL>"
	return struct.pack("!H", len(string)) + string.encode("utf-8")

def notNull(i):
	return 0 if i is None else i
def serialize(id, jso):
	if jso.get("title") is None:
		return b"\x00"
	info = jso.get("community", {}).get("statistics", {}).get("_attributes", {})
	byteData = b"\x01" + struct.pack(
				'!I IIII HH Q',
				abs(id), 
				abs(notNull(info.get("views", 0))), abs(notNull(info.get("favorites", 0))), abs(notNull(info.get("comments", 0))), abs(notNull(info.get("downloads", 0))),

				min(abs(int(notNull(jso.get("width", 0)))), 60000), min(abs(int(notNull(jso.get("height", 0)))), 60000),
				abs(int(notNull(dateutil.parser.isoparse(jso.get("pubdate", "1980-01-16T10:00:05-08:00")).timestamp())))
			)
	byteData += _serializeString(jso.get("title", ""))
	byteData += _serializeString(jso.get("type", ""))
	byteData += _serializeString(jso.get("author_name", ""))
	byteData += _serializeString(jso.get("url", ""))

	return byteData

def deserialize(byteData, offset = 0):
    isPresant = byteData[offset]
    offset+=1
    if isPresant == 0:
    	return -1, {}, offset

    id, views, favorites, comments, downloads, width, height, pubdate_timestamp = struct.unpack_from('!I IIII HH Q', byteData, offset)
    offset += struct.calcsize('!I IIII HH Q')

    title, offset = _deserializeString(byteData, offset)
    type_, offset = _deserializeString(byteData, offset)
    author_name, offset = _deserializeString(byteData, offset)
    url, offset = _deserializeString(byteData, offset)

    pubdate = datetime.datetime.fromtimestamp(pubdate_timestamp).isoformat()

    jso = {
        "community": {
            "statistics": {
                "_attributes": {
                    "views": views,
                    "favorites": favorites,
                    "comments": comments,
                    "downloads": downloads
                }
            }
        },
        "width": width,
        "height": height,
        "pubdate": pubdate,
        "title": title,
        "type": type_,
        "author_name": author_name,
        "url": url
    }
    return id, jso, offset

def bulkDecode(byteData, offset = 0):
	results = []
	while offset < len(byteData):
		idd, jso, offset = deserialize(byteData, offset)
		results.append([idd, jso])
	return results

