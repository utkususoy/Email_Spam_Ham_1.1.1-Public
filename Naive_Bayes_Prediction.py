import pickle
import creme

def naive_bayes_predict(mail):
    model_v2 = pickle.load(open("finalized_naivebayes_model_v2.sav", 'rb'))
    return model_v2.predict_one(mail)

def naive_bayes_train(mails):
    model_v2 = pickle.load(open("finalized_naivebayes_model_v2.sav", 'rb'))
    for mail,label in mails:
        model_v2 = model_v2.fit_one(mail, label)
    pickle.dump(model_v2, open("finalized_naivebayes_model_v2.sav", 'wb'))
    return model_v2

