# GithubEntitlement
Source code for running data pipeline for Github Entitlement research at CMU Strudel.

## Before we start:

### Pycharm

Writing code on the server can be quite annoying. I would recommend using the "premium" version of PyCharm and check out their "remote deployment" feature, which allows you to edit code locally and deploy it on the server easily. You could obtain a version by using your institutional email.

### TMUX

A great tool for running programs on the server so that you don't have to keep your computer on all the time.

### Perspective API 

Request a Perspective API key here: https://www.perspectiveapi.com/#/start. Don't use your CMU email account for generating keys. It doesn't work. It might be best to use a personal google email address.

### MongoDB 

You should be given a username and password to MongoDB.

To use MongoDB on the server:

```
mongo #start mongodb
use ghtorrent #choose database
db.auth("name","password") #authenticate
```


## The Data Pipeline

The data pipeine reads comments and issues collections from MongoDB database: ghtorrent, cleans the data, generates 
various features and writes generated features back into your specified collections. Currently, we are saving features for each comments and after that, aggregating comments of each issue to create features for each issue.

You can look at an example by running:

```
db.michelle_processed_comments_test.findOne() # show a processed comment
db.michelle_processed_issues_test.findOne() #show a processed issue
```
## Features

The data pipeline current generates the following text-level features for each comment in a issue, and aggregating to create features for the issue:

length of text

average length of each word

number of punctuations

number of question and exclamation marks

number of 1 letter word

number of capitalized letters

number of urls

number of tokens with non-alpha characters in the middle

number of modal words

number of unknown words as compared to dictionary 

number of emojis

number of markdowns

number of mentions

number of occurence of "+1"

number of polite words(not yet implemented)

number of insult words (improvement: could use a more complete set.)

Perspective Score

Sends processed text (check source code) to the Google Perspective score and get back a score of toxicity. For issue aggregation, an average of the top 2 toxic comments is calculated. 

Senti4SD

Uses Senti4SD to classify a comment as either positive, neutral or negative. For issue aggregation: a percentage of pos, neg, neutral comments are calculated.

Stanford Politeness API

Uses Stanford Politeness API to give a positive score and negative score. Each comment has a pair of politeness score and each issue has one. There is no aggregation here. Both are directly evaluated by the Stanford Politeness API.

## Running this data pipeline

Example usage:
``` 
python3 preprocessing.py -n -p 5 -i michelle_processed_issues_test -c michelle_processed_comments_test 
#don't repeat preprocess issues, use 5 processors. use michelle_processed_issues_test as issue collection. use michelle_processed_comments_test as comment collection.
```
Flags:

-n: short for nonrepeat. Optional. If this flag is specified, then we would not process an issue if it already exists in the specified.

-p: specifies the number of processors to use. Not Optional.

-i: collection to store processed issues. If the issue already exists in this collection, it will not be processed. Not Optional.

-c: collection to store processed comments. Not Optional.

Note: 
1. Must use `python3` to avoid Unicode error.
2. Before running the pipeline, replace all addresses to addresses in your directory.
 
## Logging.

Script running logs are stored `preprocess.log`. It stores how long each repo took to process.

## Guide to running all of these

I believe the easiest way to run this is to copy everything in my dir `/data2/michelle/GithubEntitlement` to your dir, change some of the addresses for file storage and start from there because Senti4SD script is changed to allow parallel processing and Stanford Politeness API requires a specifically configured virtual environment to run.



