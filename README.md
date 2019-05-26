# GithubEntitlement
Source code for running data pipeline for Github Entitlement research at CMU Strudel.

Before we start:

Pycharm

Writing code on the server can be quite annoying. I would recommend using the "premium" version of PyCharm and check out their "remote deployment" feature, which allows you to edit code locally and deploy it on the server easily. You could obtain a version by using your institutional email.

TMUX

A great tool for running programs on the server so that you don't have to keep your computer on all the time.

Perspective API 

Request a Perspective API key here: https://www.perspectiveapi.com/#/start. Don't use your CMU email account for generating keys. It doesn't work. It might be best to use a personal google email address.

MongoDB 

You should be given a username and password to MongoDB.

To use MongoDB on the server:

```
mongo #start mongodb
use ghtorrent #choose database
db.auth("name","password") #authenticate
   
```


Description of the data pipeline

The data pipeine reads comments and issues collections from MongoDB database: ghtorrent, cleans the data, generates 
various features and writes generated features back into your specified collections. Currently, we are saving features for each
comments and after that, aggregating comments of each issue to create features for each issue.

An example to look at is: 

Related Packages the pipeline uses to generate features:

Perspective: 

Senti4SD:

Stanford Politeness API:

In addition, here is a description of the text-level features we extract from comments.

Running this data pipeline

Use tmux. 

How long would this take.

