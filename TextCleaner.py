import string
import nltk
import re

nltk.download('stopwords')
nltk.download('punkt')

stop_words = nltk.corpus.stopwords.words('english')
ps = nltk.PorterStemmer()
wnlemma = nltk.WordNetLemmatizer()

def clean_text(text, digit_opt, return_type, root_opt):
    tokens = nltk.word_tokenize(text)
    tokens = [w.lower() for w in tokens]
#    print('Before --> {}'.format(tokens))
    if digit_opt == 'remove':
        tokens = [''.join([c for c in w if not c.isdigit()]) for w in tokens]
    if digit_opt == 'mask':
        tokens = ['digit' if w.isdigit() == True else w for w in tokens]
#        print('After --> {}'.format(tokens))
    re_punct = re.compile('[%s]' % re.escape(string.punctuation))
    tokens = [re_punct.sub('', w) for w in tokens]
    
    if root_opt == 'stemming':
        tokens = [ps.stem(w) for w in tokens if len(w) > 2]
    else:
        tokens = [wnlemma.lemmatize(w) for w in tokens if len(w) > 2]
    if return_type == 'sentence':
        return ' '.join(tokens)
    else:
        return tokens