import TextCleaner as cleaner
import string
import pandas as pd
import pickle



def count_punct(text):
    count = sum([1 for char in text if char in string.punctuation])
    return round(count / (len(text) - text.count(" ")), 3)

def get_predict(prediction_text):

    process_pred_text = pd.DataFrame([], columns=['body_len', 'punct%'])

    process_pred_text.loc['0', 'body_len'] = len(prediction_text) - prediction_text.count(' ')
    process_pred_text.loc['0', 'punct%'] = count_punct(prediction_text)

    clean_pred_text =  cleaner.clean_text(prediction_text, digit_opt='mask',
                                          root_opt= 'stemming',
                                          return_type='sentence')

    # Load pre-trained tf-idf vectorizer
    tfidf_vect_fit = pickle.load(open("tfidf.pkl", 'rb'))
    prediction_tfidf_vect = tfidf_vect_fit.transform([clean_pred_text])

    prediction_total_tfidf_vect = pd.concat([process_pred_text[['body_len', 'punct%']].reset_index(drop=True), 
                               pd.DataFrame(prediction_tfidf_vect.toarray())], axis=1)

    # Load model
    model_ = pickle.load(open("finalized_svm_model.sav", 'rb'))
    return model_.predict(prediction_total_tfidf_vect)
