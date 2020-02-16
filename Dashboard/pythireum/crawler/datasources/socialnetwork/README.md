Twitter API -> AWS Kinesis -> Aws S3 -> SpaCy-> Backend -> Fabric


!!!!
The crawler is simply reading all tweets coming from specified source and storing them in S3 (it has a buffer of 5min before pushing to s3)
The parser is using a simple NLP to extract the entities from all stored tweets.
It uses the methods in the nlp_helper class (there is one for french and one for english but both should be improved).
!!!!


Now everything is setup:
You can create a Kinesis stream to follow some users and track only specific terms :

Get user Id you want to follow and put it in stream.filter(follow=)
https://tweeterid.com/

See patterns of track :
https://developer.twitter.com/en/docs/tweets/rules-and-filtering/overview/standard-operators.html

More information
https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters


Tests (https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
):
- Putting track and followed show all tweet from anyone which contains track (doesn't seems to take into account follow)
- Putting only follow=['UserId'] permits to follow twitter from users (will get all tweets from the users?)