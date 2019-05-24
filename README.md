# GithubEntitlement
Source code for running data pipeline for Github Entitlement research at CMU Strudel.

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

