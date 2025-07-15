from flask import Flask, jsonify, request
import numpy as np

app = Flask(__name__)

def hormone_levels(day):
    max_estrogen = 200
    min_estrogen = 50
    max_progesterone = 25
    min_progesterone = 1

    estrogen = min_estrogen + (max_estrogen - min_estrogen) * np.sin(np.pi * day / 28)

    if day < 14:
        progesterone = min_progesterone
    else:
        progesterone = min_progesterone + (max_progesterone - min_progesterone) * np.sin(np.pi * (day - 14) / 14)

    return estrogen, progesterone

@app.route('/hormone_levels', methods=['POST'])
def get_hormone_levels():
    data = request.get_json()
    day = data['day']
    estrogen, progesterone = hormone_levels(day)
    return jsonify({'estrogen': estrogen, 'progesterone': progesterone})

if __name__ == '__main__':
    app.run(debug=True)
