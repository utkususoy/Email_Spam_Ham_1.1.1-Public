import pymongo
from dotenv import load_dotenv
import os

load_dotenv() # use dotenv to hide sensitive credential as environment variables

DATASET_URL=f'mongodb+srv://utkususoy:{os.environ.get("mongo_pass")}@cluster0.rknag.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'

#Establish Database Connection
client = pymongo.MongoClient(DATASET_URL)
db = client['spamdb']

def remove_all_mails():
    db['spamdb'].delete_many({})
    return "ok"

# Sadece yanlış predict edilenler insert edilir
def insert_one_mail(data):
    mails = get_all_mails()
    if data['mail'] not in mails:
        db['spamdb'].insert_one({"mail": data['mail'], "pred": data['prediction'] , "val": data['validation']})
    else:
        print("Duplicate mail")

    # Add all mails to Loggs Cluster regardless the repetitaion
    db['Loggs'].insert_one({"mail": data['mail'], "pred": data['prediction'],"val": data['validation']})
    return "ok"

# Move all mails to Trained collection which are trained
def copy_mails(mails):
    for mail in mails:
        db['Trained'].insert_one({"mail": mail[0], "label": mail[1]})
    remove_all_mails()
    return "ok"

def get_all_mails():
    mails = []
    for mail_ in db['spamdb'].find({}, { "_id": 0, "mail": 1 }):
        mails.append(mail_['mail'])
    return mails

def get_all_invalid_mails():
    mails = []
    for mail_ in db['spamdb'].find({}, { "_id": 0, "mail": 1, "pred":1, "val": 1}):
        if mail_["val"] != mail_["pred"]:
            mails.append((mail_['mail'], mail_['val']))
    return mails

def get_all_logs():
    mails = []
    for mail_ in db['Loggs'].find({}):
        mails.append(mail_)
    return mails

def get_all_valid_unique_logs():
    mails = []
    for mail_ in db['Loggs'].find({}, { "_id": 0, "mail": 1, "pred":1, "val": 1}):
        if mail_['val'] == mail_['pred'] and (mail_['mail'] not in mails):
            mails.append(mail_)
    return mails

def model_customer_accuracy():

    general_accuracy = 0
    current_model_accuracy = 0
    # Current Model Evaluation
    current_total_mails = len(get_all_mails())
    current_invalid_mails = len(get_all_invalid_mails())
    current_valid_mails = current_total_mails - current_invalid_mails
    try:
        current_model_accuracy = (current_valid_mails / current_total_mails) * 100
    except:
        current_model_accuracy = 0

    total_all_mails = len(get_all_logs())
    total_valid_mails = len(get_all_valid_unique_logs())
    try:
        general_accuracy = (total_valid_mails / total_all_mails) * 100
    except:
        general_accuracy = 0

    return general_accuracy, current_model_accuracy

#Steps
#1-insert_one
#2-move_all change to move_invalids mails to Trained
#3-move_all mails to Loggs
#3-remove_all