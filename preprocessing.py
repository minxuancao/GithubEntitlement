'''
takes data from mongoDB, preprocess them and  put into mySQL
reference: https://medium.com/@saksham.malhotra2196/the-efficient-way-of-using-multiprocessing-with-pymongo-a7f1cf72b5b7
'''
from functools import partial
from pymongo import MongoClient
import TextParser
from perspective import Perspective
import pandas as pd
import subprocess
import multiprocessing as mp
import time
import ast
import logging
import heapq
import sys
from bs4 import BeautifulSoup
import bs4
import pickle
import nltk.data
import argparse


#global variable
senti4SD_address = "Senti4SD/ClassificationTask/"
senti4SD_abs_address = "/data2/michelle/GithubEntitlement/Senti4SD/ClassificationTask/"
core_nlp_address = "/data2/michelle/GithubEntitlement/stanford-corenlp-full-2014-10-31/" #set core_nlp address
core_nlp_parse_address = "/data2/michelle/GithubEntitlement/stanford-corenlp-full-2014-10-31/parse/"
core_nlp_pickle_address = "/data2/michelle/GithubEntitlement/stanford-corenlp-full-2014-10-31/pickles/"
politness_env = "/data2/michelle/GithubEntitlement/politeness/venv/bin/python" #address of stanford politeness running environment
politeness_address = "/data2/michelle/GithubEntitlement/politeness/"
stanford_politeness_score_address = "/data2/michelle/GithubEntitlement/politeness/scores/"

def connect_Mongo():
    client = MongoClient(maxPoolSize=10000)
    db = client.ghtorrent
    db.authenticate(name="ght",password="ght")
    return db

def get_perspective_score(text):
    API_KEY = "AIzaSyBpqnKD1eyFU5BBkSvP4qQp6azbc6iNmNU"
    p = Perspective(API_KEY)
    try:
        comment = p.score(text,tests=["TOXICITY"])
        score = comment["TOXICITY"].score
    except:
        score = 0
    return score

#takes in the address of classificationTask.sh
#the name of the input csv
#the name of the output csv
#return a list of classification by order
#note: changed classificationTask.sh so that features are saved in different files
def get_senti4SD(input_filename,output_filename,feature_filename,addr=senti4SD_address):
    #run sh
    try:
        subprocess.check_call(['sh', addr+"classificationTask.sh",addr+input_filename,output_filename,feature_filename])
    except subprocess.CalledProcessError:
        sys.stderr.write("subprocess exception in Senti4SD")
    #read results
    df = pd.read_csv(addr+output_filename)

    #sort by "Row"
    df = df.sort_values(by=['Row'])

    return df.Predicted.tolist()

#output_addr: "path/name.pickle"
#total text: total text concatentad
#comment_l: a list of number of sentences in each comment

#think more about inputs!!!
def coreNLP_parse(input,comment_l):
    try:
        subprocess.check_call(['java','-cp',core_nlp_address+"*",'edu.stanford.nlp.pipeline.StanfordCoreNLP',
                               '-annotators','tokenize,ssplit,parse','-file',senti4SD_abs_address+input,'-outputDirectory',core_nlp_parse_address])
    except subprocess.CalledProcessError:
        sys.stderr.write("subprocess exception")

    with open(senti4SD_abs_address+input,'r') as f:
        total_text = f.read()

    documents = [] #stores parse for the issue level and comment level.  The first doc is issue level, others are on comment level

    #sentences
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = sent_detector.tokenize(total_text.strip()) #get total_text

    ## parse xml
    parses = []  # stores parses for each sentence
    with open(core_nlp_parse_address+input+".xml",'r') as f:
        soup = BeautifulSoup(f, "lxml-xml")
        dependencies = soup.find_all('dependencies', {"type": "collapsed-dependencies"})
        for d in dependencies:  # for each sentence
            sentence_parse = []
            for c in d.children:
                if isinstance(c, bs4.element.Tag):
                    type = c.attrs['type']
                    l = c.text.split()
                    pair = "%s(%s-%s, %s-%s)" % (type, l[0], c.governor['idx'], l[1], c.dependent['idx'])
                    sentence_parse.append(pair)
            parses.append(sentence_parse)

    #add to total_text document
    document = {
        "text": total_text,
        "sentences": sentences,
        "parses": parses,
    }
    documents.append(document)

    #add a document for each comment
    start = 0
    for comment_number in comment_l:
        document = {
            "text": ' '.join(sentences[start:start+comment_number]),
            "sentences": sentences[start:start+comment_number],
            "parses": parses[start:start+comment_number],
        }
        documents.append(document)
        start+=comment_number

    #write list to pickle
    #add a address for the pickle file
    with open(core_nlp_pickle_address+input+".pkl",'wb') as f:
        pickle.dump(documents, f,protocol=2) # set protocol to 2 so that it could read by python 2.7, which is the env we use for running


#return politeness score for total text and each comment
def calculate_stanford_politeness_score(input,output):
    #call model.py with input and output
    try:
        subprocess.check_call([politness_env,politeness_address+"model.py",core_nlp_pickle_address+input+".pkl",stanford_politeness_score_address+output])
    except subprocess.CalledProcessError:
        sys.stderr.write("subprocess exception")


#return a json object to be stored in mongoDB
def process_comment(doc):

    text = doc["body"]
    if TextParser.contain_non_english(text): # if the text contains non-english, we terminate early
        return {
            "valid": False,
            "num_reference": 0,
           "num_url": 0,
           "num_emoji": 0,
           "num_mention": 0,
           "num_plus_one": 0,
           "perspective_score": 0,
           "text": ""};

    num_reference = TextParser.count_reference_line(text)
    # print("num_reference: %d" % num_reference)
    text = TextParser.remove_reference(text)
    # print("text 0: %s" % text)

    text = TextParser.transform_markdown(text)  # use mistune to transform markdown into html for removal later.
    # print("text 1: %s" % text)

    text = TextParser.remove_inline_code(text)  # used place-holder: InlineCode
    # print("text 2: %s" % text)

    text = TextParser.remove_html(text)
    # print("text 3: %s" % text)

    num_url = TextParser.count_url(text)
    # print("num_url: %d" % num_url)
    text = TextParser.remove_url(text)
    # print("text 4: %s" % text)

    num_emoji = TextParser.count_emoji(text)
    # print("num_emoji: %d" % num_emoji)
    text = TextParser.remove_emoji_marker(text)  # remove the two semi-colons on two sides of emoji
    # print("text 5: %s" % text)
    text = TextParser.remove_newline(text)
    # print("text 6: %s" % text)

    num_mention = TextParser.count_mention(text)
    # print("num_mention: %d" % num_mention)
    text = TextParser.replace_mention(text)
    # print("text 7: %s" % text)
    # sub all "+1" to "plus one"
    num_plus_one = TextParser.count_plus_one(text)
    # print("num_plus_one: %d" % num_plus_one)
    text = TextParser.sub_PlusOne(text)
    # print("text 8: %s" % text)

    perspective_score = get_perspective_score(text)

    return {
            "_id": "%s/%s/%d/%d" % (doc["repo"], doc["owner"], doc["issue_id"], doc["id"]),
            "repo": doc["repo"],
            "owner": doc["owner"],
            "issue_id": doc["issue_id"],
            "comment_id": doc["id"],
            "valid": True,
            "num_reference": num_reference,
           "num_url": num_url,
           "num_emoji": num_emoji,
           "num_mention": num_mention,
           "num_plus_one": num_plus_one,
           "perspective_score": perspective_score,
           #"text": text.decode("utf-8")
            "text": text}

def consumer(repo,non_repeat):

    db = connect_Mongo()

    query_dict = ast.literal_eval(repo)
    query_dict["pull_request"] = {'$exists':False}
    issue_ids = db.issues.find(query_dict).distinct('number') #query issue id #where the issue is not a pull request, then don't need to fitlering
    #logging.info(query_dict)
    query_dict.pop("pull_request") #remove "pull_request" key

    for issue_id in issue_ids:

        # check to see if the issue is already processed
        if non_repeat:
            id = "%s/%s/%d" % (query_dict["repo"], query_dict["owner"], issue_id)
            if db.michelle_processed_issues_test.find_one({"_id":id}):
                logging.info("%s already processed" % id)
                continue

        #query all comments.
        issue_start = time.time();

        query_dict["issue_id"] = issue_id # set issue_id for querying

        comments = db.issue_comments.find(query_dict)
        #set a data struc to store everything

        # take the top2 for perspective score; use a heap
        perspective_scores = []
        # concat text

        total_comment_info = {
            "total_reference": 0,
            "total_url": 0,
            "total_emoji": 0,
            "total_mention": 0,
            "total_plus_one": 0,
            "total_text": "",
        }

        #Senti4SD document preparation
        input_senti4sd_filename = "input_%s_%s_%d.csv" % (query_dict["owner"],query_dict["repo"],issue_id)
        output_senti4sd_filename = "output_%s_%s_%d.csv" % (query_dict["owner"], query_dict["repo"], issue_id)
        feature_senti4sd_filename = "extractedFeatures_%s_%s_%d.csv" % (query_dict["owner"], query_dict["repo"], issue_id)
        f = open(senti4SD_address+input_senti4sd_filename,'w')

        comment_info_l = []
        comment_sentence_l = []
        # process comments
        for comment in comments:

            logging.debug("Issue id: %d Comment: %s " % (issue_id,comment))

            comment_info = process_comment(comment)

            if not comment_info["valid"]: #if comment is not valid, go to next loop
                continue

            comment_info_l.append(comment_info) #add valid comment_info into a list

            sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
            sentences = sent_detector.tokenize(comment_info["text"].strip())
            comment_sentence_l.append(len(sentences))

            total_comment_info["total_reference"] += comment_info["num_reference"]
            total_comment_info["total_url"] += comment_info["num_url"]
            total_comment_info["total_emoji"] += comment_info["num_emoji"]
            total_comment_info["total_mention"] += comment_info["num_mention"]
            total_comment_info["total_plus_one"] += comment_info["num_plus_one"]

            if len(perspective_scores) > 2:
                if min(perspective_scores) < comment_info["perspective_score"]:
                    _ = heapq.heappushpop(perspective_scores,comment_info["perspective_score"])
            else:
                perspective_scores.append(comment_info["perspective_score"])
            #write all comments to 1 part
            if total_comment_info["total_text"] == "":
                total_comment_info["total_text"] += comment_info["text"]
            else:
                total_comment_info["total_text"] += " " + comment_info["text"]
            f.write(comment_info["text"]+"\n") #write to csv

        #close input senti4sd file
        f.close()

        #check total_text here, it is empty skip the rest!!!
        if total_comment_info["total_text"] == "": #too little text, no need to write into database
            continue

        if len(perspective_scores):
            total_comment_info["perspective_score"] = sum(perspective_scores)/len(perspective_scores)
        else:
            total_comment_info["perspective_score"] = 0
        #aggregate some features on the issue level ###!!! may need to change this part !!!###
        total_comment_info["length"] = TextParser.get_length(total_comment_info["total_text"])
        total_comment_info["avg_word_length"] = TextParser.get_avg_length(total_comment_info["total_text"])
        total_comment_info["num_punct"] = TextParser.count_punct(total_comment_info["total_text"])
        total_comment_info["num_QEMark"] = TextParser.count_QEMark(total_comment_info["total_text"])
        total_comment_info["num_one_letter_word"] = TextParser.count_one_letter(total_comment_info["total_text"])
        total_comment_info["num_capital"] = TextParser.count_captial(total_comment_info["total_text"])
        total_comment_info["num_non_alpha_in_middle"] = TextParser.count_non_alpha_in_middle(total_comment_info["total_text"])
        total_comment_info["num_modal_word"] = TextParser.count_modal_word(total_comment_info["total_text"])
        total_comment_info["num_unknown_word"] = TextParser.count_unknown_word(total_comment_info["total_text"])
        total_comment_info["num_insult_word"] = TextParser.count_insult_word(total_comment_info["total_text"])

        #sent to Senti4SD for score, we would want a result for each comment
        senti_start = time.time()
        senti_l = get_senti4SD(input_senti4sd_filename,output_senti4sd_filename,feature_senti4sd_filename) #change this to returning a list

        # for each comment_info add a senti4sd classification
        for i in range(len(senti_l)):
            comment_info_l[i]["senti_4sd"] = senti_l[i]

        #calculate an aggregation
        total_comment_info["senti4sd_positive_percentage"] =  senti_l.count("positive")/len(senti_l)
        total_comment_info["senti4sd_neutral_percentage"] = senti_l.count("neutral")/len(senti_l)
        total_comment_info["senti4sd_negative_percentage"] = senti_l.count("negative")/len(senti_l)

        #logging.info("senti4sd took %d" % (time.time()-senti_start))

        #stanford politeness API
        politeness_start = time.time()
        #make a pickle file using coreNLP
        coreNLP_parse(input_senti4sd_filename,comment_sentence_l) #comment_l is a list that stores number of sentences each comment has

        #pass this pickle to stanford politeness api
        calculate_stanford_politeness_score(input_senti4sd_filename,output_senti4sd_filename)

        #read from csv the score, the first one is for total, then for each comment
        score_df = pd.read_csv(stanford_politeness_score_address+output_senti4sd_filename,header=None)
        for row in score_df.itertuples():
            if row.Index == 0:
                total_comment_info["stanford_positive"] = row._1
                total_comment_info["stanford_negative"] = row._2
            else:
                comment_info_l[row.Index-1]["stanford_positive"] = row._1
                comment_info_l[row.Index-1]["stanford_negative"] = row._2

        #logging.info("stanford took %d" % (time.time()-politeness_start))

        #set_id
        total_comment_info["repo"] = query_dict["repo"]
        total_comment_info["owner"] = query_dict["owner"]
        total_comment_info["issue_id"] = query_dict["issue_id"]
        total_comment_info["_id"] = "%s/%s/%d" % (query_dict["repo"],query_dict["owner"],query_dict["issue_id"])

        #log for checking to somewhere, not multi-process safe
        #logging.debug(total_comment_info)

        # insert total_comment_info to database
        db.michelle_processed_issues_test.replace_one({"_id":total_comment_info["_id"]},total_comment_info,upsert=True)

        # insert each comment_info to database
        for comment_info in comment_info_l:
            db.michelle_processed_comments_test.replace_one({"_id":comment_info["_id"]},comment_info,upsert=True)
        #logging.info("%s processing took %d" % (query_dict, time.time() - issue_start))

    return query_dict


if __name__ == "__main__":
    #config logging
    logging.basicConfig(filename='preprocess.log',filemode='w',format='%(name)s - %(levelname)s - %(message)s',level=logging.INFO)

    non_repeat = False

    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--nonrepeat", help="does not recaluculate documents already in collections",action="store_true")
    args = parser.parse_args()
    if args.nonrepeat:
        logging.info("non-repeat is turned on")
        non_repeat = True

    # read in the needed repos
    repo_df = pd.read_csv("issues_by_reporter_2017_stratified.csv")
    repos = repo_df["find_str"][-3:] #take the last 3 elements

    # iterate through my collection to preprocess
    num_process = 2
    pool = mp.Pool(processes=num_process)

    start = time.time()
    chunk_size = 1 # set a large chunksize when repos is large!!!
    for repo in pool.imap_unordered(partial(consumer,non_repeat=non_repeat),repos):
        logging.info("Processing %s took %d s " % (repo, time.time()-start))
    pool.close()


    # for repo in repos:
    #     logging.info("Started Processing: %s" % (repo))
    #     start = time.time()
    #     consumer(repo,non_repeat)
    #     end = time.time()
    #     logging.info("Finished Processing: %s ; time took: %d" % (repo,(end-start)))





    # limited = 10000 # limit to 10,000 documents
    # skipped = 0
    #
    # while True:
    #
    #     if skipped > document_count:
    #         break
    #
    #     cursor = db.issue_comments.find({"owner": "MicrosoftDocs","repo":"azure-docs"}).skip(skipped).limit(limited);
    #
    #     result = pool.map(consumer,cursor); #func
    #     results.extend(result)
    #
    #     skipped += limited
    #     print("[-] Skipping {}".format(skipped))
    #
    # print(len(results))

    # #write df['text'] to csv
    # csv_addr = "Senti4SD/ClassificationTask/" #probably change to cur dir...
    # df['text'].to_csv(csv_addr+"entitlement.csv",index=False)
    # #run senti4sd
    # df['senti4sd'] = get_senti4SD(csv_addr,"entitlement.csv")
    # # add line to data frame
    # df.to_csv("preprocessed.csv",encoding='utf-8')
    # #close the connection
    # print("closing connection!")
    # client.close()



