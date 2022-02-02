import pymongo
from dotenv import load_dotenv
import os
import datetime
import pickle

load_dotenv() # use dotenv to hide sensitive credential as environment variables

class Mongo_db_repository:

    def __init__(self):
        self.client = pymongo.MongoClient({os.environ.get("DATABASE")})
        self.db = self.client['spamdb']

    def remove_all_mails(self):
       self.db['spamdb'].delete_many({})
       return "ok"

    # Spam yada non-spam olup olmaması önemsiz tek kural var oda aynı maillerin repetition olmicak
    def insert_one_mail(self, data):
        #Establish Database Connection

        mails = self.get_all_mails()
        if data['mail'] not in mails:
            self.db['spamdb'].insert_one({"mail": data['mail'], "pred": data['prediction'] , "val": data['validation']})
        else:
            print("Duplicate mail")

        # Add all mails to Loggs Cluster regardless the repetitaion
        self.db['Loggs'].insert_one({"mail": data['mail'], "pred": data['prediction'],"val": data['validation']})
        return "ok"

    # Move all mails to Trained collection which are trained
    def copy_mails(self, mails):
        for mail in mails:
            self.db['Trained'].insert_one({"mail": mail[0], "label": mail[1]})
        self.remove_all_mails()
        return "ok"

    def get_all_mails(self):
        mails = []
        for mail_ in self.db['spamdb'].find({}, { "_id": 0, "mail": 1 }):
            mails.append(mail_['mail'])
        return mails

    def get_all_invalid_mails(self):
        mails = []
        print(self.get_all_mails())
        for mail_ in self.db['spamdb'].find({}, { "_id": 0, "mail": 1, "pred":1, "val": 1}):
            if mail_["val"] != mail_["pred"]:
                mails.append((mail_['mail'], mail_['val']))
        return mails

    def get_all_logs(self):
        mails = []
        for mail_ in self.db['Loggs'].find({}):
            mails.append(mail_)
        return mails

    def get_all_valid_unique_logs(self):
        mails = []
        for mail_ in self.db['Loggs'].find({}, { "_id": 0, "mail": 1, "pred":1, "val": 1}):
            if mail_['val'] == mail_['pred'] and (mail_['mail'] not in mails):
                mails.append(mail_)
        return mails

    def get_model(self):
    #    loaded_model = self.db['Models'].find({})
    #    json_data = {}
    #    for i in loaded_model:
    #        json_data = i

    #    pickled_model = json_data['model_obj']
    #    ml_model = pickle.loads(pickled_model)
    #    return ml_model
        loaded_byte_model = [self.db['Models'].find({})][-1]

        json_data = {} 
        for i in loaded_byte_model:
            json_data = i

        print(json_data['_id'])
        pickled_model = json_data['model_obj']
        ml_model = pickle.loads(pickled_model)
    
        return ml_model

    def save_model(self, ml_model):
    #    pickled_model = pickle.dumps(ml_model)
    #    self.db['Models'].delete_many({})
    #    self.db['Models'].insert_one({'model_obj': pickled_model, 'date': datetime.datetime.now(), 'name': 'tweaked'})
        datetimes_list = []
        for model_obj in self.db['Models'].find({}, {'_id': 1, 'model_obj': 1, 'date': 1, 'name': 1}):
            datetimes_list.append(model_obj)
        if len(datetimes_list) == 4:
            self.db['Models'].delete_one({'name':'new'}) # delete model-object which placed in second 
        byte_model = pickle.dumps(ml_model) # Convert bytes object
        self.db['Models'].insert_one({'model_obj': byte_model, 'date': datetime.datetime.now(), 'name': "new"}) # add new model to end of collection
        return byte_model



    def model_customer_accuracy(self):

        general_accuracy = 0
        current_model_accuracy = 0
        # Current Model Evaluation
        current_total_mails = len(self.get_all_mails())
        current_invalid_mails = len(self.get_all_invalid_mails())
        current_valid_mails = current_total_mails - current_invalid_mails

        try:
            current_model_accuracy = (current_valid_mails / current_total_mails) * 100
        except:
            current_model_accuracy = 0

        total_all_mails = len(self.get_all_logs())
        total_valid_mails = len(self.get_all_valid_unique_logs())
        try:
            general_accuracy = (total_valid_mails / total_all_mails) * 100
        except:
            general_accuracy = 0

        return general_accuracy, current_model_accuracy

