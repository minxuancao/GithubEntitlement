import re
import nltk
from nltk.corpus import words
from nltk.stem import WordNetLemmatizer
import mistune
from langdetect import detect
'''preprocess data for input'''

# remove previously referenced comments
#remove every line that starts with ">"
def remove_reference(text):
    pattern = r'''^>.*'''
    result = re.sub(pattern, "", text, 0, re.MULTILINE | re.IGNORECASE | re.VERBOSE)
    return result

#Note: does not work well with short senteces.
#Note: does not work well with short senteces.
def contain_non_english(text):
    try:
        return detect(text) != "en"
    except:
        return True  #if can't detect return true

# an edge case to deal with
'''
```yml
    staticDir:
      - "static"
      - "../dist"
    ```
'''
def remove_markdown(text):
    pattern = r"""
        ^(?:\ {4}.+\n)+(?!)         # Ignore content of all indented text
        |(^```(?:[^`]+|`(?!``))*```)  # Do not stop at single ` backticks within ```...``` blocks
        |(```.+?```) # remove inline ```...```
        """
    #why doesn't work if we remove ^
    result = re.sub(pattern, "MarkdownCode", text, 0, re.MULTILINE | re.IGNORECASE | re.VERBOSE)
    return result

def transform_markdown(text):
    return mistune.markdown(text)

def remove_html(text):
    pattern = r'''<[^>]*>'''
    result = re.sub(pattern, "", text, 0, re.MULTILINE | re.IGNORECASE | re.VERBOSE)
    return result


#replace inline highlighted code with text
def remove_inline_code(text):
    pattern = r'''(`.+?`)'''
    result = re.sub(pattern, "InlineCode", text, 0, re.MULTILINE | re.IGNORECASE | re.VERBOSE)
    return result

def remove_empty_space(text):
    pass

def sub_PlusOne(text):
    pattern = r"""(\+1)"""
    result = re.sub(pattern,"plus one", text,0,re.MULTILINE | re.IGNORECASE | re.VERBOSE)
    return result

#remove @
def replace_mention(text):
    pattern = r'''@[A-Za-z0-9-]+''' # remove @
    result = re.sub(pattern, "@friend", text, 0, re.MULTILINE | re.IGNORECASE | re.VERBOSE)
    return result


def remove_url(text):
    pattern = r'''https?://[^ ]+'''
    result = re.sub(pattern, "", text, 0, re.MULTILINE | re.IGNORECASE | re.VERBOSE)
    return result

def remove_newline(text):
    #text = text.encode('utf-8').replace('\n', ' ').replace('\r', '').replace('\t','')
    text = text.replace('\n', ' ').replace('\r', '').replace('\t', '')
    return text

# just remove all :
def remove_emoji_marker(text):
    # pattern = r''':(.+?):'''
    # m = re.search(pattern, text)
    # replacement = ""
    # if m:
    #     replacement =  (m.group(1))
    # text = re.sub(pattern,replacement,text,0,re.MULTILINE | re.IGNORECASE | re.VERBOSE)

    pattern = r''':'''
    text = re.sub(pattern, "", text, 0, re.MULTILINE | re.IGNORECASE | re.VERBOSE)
    return text

#has probelms. Deal with this later. Removing letters that are not supposed to be removed
def remove_emoji(text):
    pattern = r"""
	[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F1E0-\U0001F1FF]|[\U00002702-\U000027B0]|[\U000024C2-\U0001F251]
	"""
    result = re.sub(pattern,"",text,0,re.MULTILINE | re.IGNORECASE | re.VERBOSE)
    return result

#################### Extracting textual features ####################

# get length of text in tokens
def get_length(text):
    return len(text)


# get average length of word
def get_avg_length(text):
    word_length_lst = [len(word) for word in text.split(' ')]
    return sum(word_length_lst) / len(word_length_lst)


# get number of punctuations
def count_punct(text):
    pattern = r'[!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]'
    sentences = re.findall(pattern, text)
    return len(sentences)


# get number of periods, question marks,quotes, and repeated punctuation
def count_QEMark(text):
    pattern = r'[!?]'
    return len(re.findall(pattern, text))


# get number of 1 letter tokens
def count_one_letter(text):
    # split by space
    pattern = r'(^|\W)[a-zA-Z](\W|\Z)'
    l = re.findall(pattern, text)
    return len(l)


# get number of capitalized letters
def count_captial(text):
    pattern = r'[A-Z]'
    return len(re.findall(pattern, text))


# get number of URLs
def count_url(text):  # check for http:// or https://
    pattern = r'https?://[^ ]+'
    return len(re.findall(pattern, text))


# get number of tokens with non-alpha characters in the middle???
def count_non_alpha_in_middle(text):
    pattern = r'(^|\w)[!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~](\w|\Z)'
    return len(re.findall(pattern, text))

# get number of politeness words
def count_politeness_words(text):
    pass

# get number of modal words
def count_modal_word(text):
    #text = text.decode("utf-8") #decode to utf-8 to avoid ascii problem
    text = nltk.word_tokenize(text)
    tag_lst = nltk.pos_tag(text)
    return len([(w, t) for (w, t) in tag_lst if t == 'MD'])

# get number of unknown words as compared to dictionary
def count_unknown_word(text):
    #text = text.decode("utf-8") #decode to utf-8 to avoid ascii problem
    text = nltk.word_tokenize(text)
    unknown_lst = [word for word in text if word not in words.words()]
    return len(unknown_lst)

# get number of insult and hate blacklist words
# May not be the most relevant source: https://www.cs.cmu.edu/~biglou/resources/bad-words.txt
# but we could substitute this later if needed
def count_insult_word(text):
    #open file
    bad_file_addr = "bad-words.txt"
    num_insult_word = 0
    with open(bad_file_addr) as f:
        bad_word_l = f.read().strip().split()
    for w in text:
        if w in bad_word_l:
            num_insult_word+=1
    return num_insult_word

# count number of reference lines
def count_reference_line(text):
    pattern = r'''^>.*'''
    return len(re.findall(pattern,text,re.MULTILINE | re.IGNORECASE | re.VERBOSE))


# count number of emojis
def count_emoji(text):
    pattern = r''':([a-zA-Z]+?):'''
    return len(re.findall(pattern,text,re.MULTILINE | re.IGNORECASE | re.VERBOSE))

# count number of markdown lines
def count_markdown(text):
    pattern = r"""
            ^(?:\ {4}.+\n)+(?!)         # Ignore content of all indented text
            |(^```(?:[^`]+|`(?!``))*```)  # Do not stop at single ` backticks within ```...``` blocks
            |(```.+?```) # remove inline ```...```
            """
    return len(re.findall(pattern, text, re.MULTILINE | re.IGNORECASE | re.VERBOSE))

#count number of mentions
def count_mention(text):
    pattern = r'''@[A-Za-z0-9-]+'''  # remove @
    return len(re.findall(pattern, text, re.MULTILINE | re.IGNORECASE | re.VERBOSE))

#count number of plus ones
def count_plus_one(text):
    pattern = r"""(\+1)"""
    return len(re.findall(pattern, text, re.MULTILINE | re.IGNORECASE | re.VERBOSE))
