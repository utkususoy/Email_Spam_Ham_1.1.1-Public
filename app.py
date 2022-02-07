from crypt import methods
from distutils.log import debug
import re
from unittest import result
from flask import Flask, jsonify, request, render_template
import Naive_Bayes_Prediction
import repository
import pickle
import requests
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
res = ""


@app.route("/")
def welcome_page():
    return render_template("index.html")

@app.route("/model", methods=['POST'])
def receive_text():

    try:
        global res

        request_data = request.form["pred_text"]

    #   repository.insert_one_mail(request_data)
    # modeli çagırıp predict ettir.
        result = Naive_Bayes_Prediction.naive_bayes_predict(request_data)
        print("received {}".format(result))
        return render_template('evaluate.html', res = {"res":result, "mail":request_data}) #changed
    except Exception as e:
        return "{}".format(e)

####

#    Sadece Yanlış predict edilen mailler tekrardan train edilecek. Değiştir mail repetition olmasın sadece

        ####
@app.route("/train", methods=['GET'])
def train_model():
    repo = repository.Mongo_db_repository()
    # 1-Get all incorrect mails (Receive only invalid mails)
    mails = repo.get_all_invalid_mails()
    # 2-re-Train all

    model_v2 = Naive_Bayes_Prediction.naive_bayes_train(mails)

    repo.copy_mails(mails)

    return {"ok": mails}

@app.route("/save", methods=['POST'])
def evaluate():
    repo = repository.Mongo_db_repository()

    request_datav2 = request.get_json()
    print(request_datav2)
    repo.insert_one_mail(request_datav2)
    return "ok"

@app.route("/eval", methods=['GET'])
def get_user_accuracy():
    repo = repository.Mongo_db_repository()
    general_acc, current_model_acc = repo.model_customer_accuracy()
    return {'runtime_acc': general_acc, 'model_acc': current_model_acc}


scheduler = BackgroundScheduler()
scheduler.add_job(func=train_model, trigger="interval", seconds=60)
scheduler.start()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 8000, use_reloader=False)