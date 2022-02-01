from crypt import methods
from distutils.log import debug
import re
from unittest import result
from flask import Flask, jsonify, request, render_template
import Naive_Bayes_Prediction
import repository

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

@app.route("/train", methods=['GET'])
def train_model():
    # 1-Get all incorrect mails (Receive only invalid mails)

    mails = repository.get_all_invalid_mails()
    # 2-re-Train all
    repository.copy_mails(mails)


    return "ok"

@app.route("/save", methods=['POST'])
def evaluate():

    request_datav2 = request.get_json()
    print(request_datav2)
    repository.insert_one_mail(request_datav2)
    return "ok"

@app.route("/eval", methods=['GET'])
def get_user_accuracy():
    general_acc, current_model_acc = repository.model_customer_accuracy()
    return {'runtime_acc': general_acc, 'model_acc': current_model_acc}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 80, debug=True)