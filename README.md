# Deviant Clone

Abuse the DeviantArt `oembed` api to make a clone of the website in only about 6 gigabytes. DeviantArt counts it's id numbers up incrementally, and therefore you can theoretically clone the entire website. As of the time of writing, DeviantArt is at about 1.1 **billion** posts, and therefore speed is key.

In order to download the entire website it requires many threads running on many machines with hyper efficant code, and that is what the goal of this repo is. This repo contains 2 main programs, the server, and the runner. The server manages what range of id numbers the the runner is fetching, then posts the gziped data back to the server. The resulting data is in a custom binary format, allowing for the average deviation post to be around 55 bytes once gziped. 

## The api
By simply going to the following url, you can view most of the important metadata for a post.

```plaintext
https://backend.deviantart.com/oembed?url=123456
``` 

## Legal
```plaintext
Copyright (c) 2024 HeronErin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

