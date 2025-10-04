# ImageUploader
This is a test project written completely in Python using Fastht.ml to accomplish as much as possible. My goal at the onset
was to write this program without any Javascript, but in the end I caved and wrote about 15-20 lines. Mostly this was dues to
the return of status 204 with no body from the post to S3.  This was technically developed against Railway's Object Storage, 
but there should be no differences if you were to use AWS directly according to their docs.  

## Running
Simply run python main.py and the server will come up.

## Deployment
I tried Railway for the first time recently and this made it super easy.  As noted above I actually used their Object Storage
feature instead of my own S3 bucket.  Deployment was trivial to configure and is triggered by every merge to main automatically.
This was as close to seamless as I have seen in a long time.  I am not sponsored, but I would encourage you to go to
[https://railway.com](https://railway.com) or go with my referral link in it [https://railway.com?referralCode=OeVSht](https://railway.com?referralCode=OeVSht)
