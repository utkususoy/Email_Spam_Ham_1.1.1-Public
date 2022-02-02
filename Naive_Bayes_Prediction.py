import pickle
import creme
import os
import repository


def naive_bayes_predict(mail):
#    model_v2 = pickle.load(open("finalized_naivebayes_model_v2.sav", 'rb'))
    repo = repository.Mongo_db_repository()
    model_v2 = repo.get_model()
    return model_v2.predict_one(mail)

def naive_bayes_train(mails):
#    model_v2 = pickle.load(open("finalized_naivebayes_model_v2.sav", 'rb'))
    repo = repository.Mongo_db_repository()
    model_v2 = repo.get_model()
    for mail,label in mails:
        model_v2 = model_v2.fit_one(mail, label)
#    if os.path.exists("finalized_naivebayes_model_v2.sav"):
#        os.remove("finalized_naivebayes_model_v2.sav")
#    pickle.dump(model_v2, open("finalized_naivebayes_model_v2.sav", 'wb'))
    model_v3 = repo.save_model(model_v2)
    return model_v3

