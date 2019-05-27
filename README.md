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


Related Packages the pipeline uses to generate features:

Perspective: 

Senti4SD:

Stanford Politeness API:

In addition, here is a description of the text-level features we extract from comments.

Running this data pipeline

Use tmux. 

How long would this take.

