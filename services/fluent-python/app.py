# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# app.py
# 
# Attributions: 
# [1] 
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.08.28'
"""app.py: 

{Description}
"""

import os
from fluent import sender, event
from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)

CORS(app)

fluent_host = os.environ.get('FLUENT_HOST')
sender.setup('fluent-python.test', host=fluent_host, port=24224)


@app.route('/log', methods=['POST'])
def log():
    response = {'status': 'fail', 'log': ''}

    data = request.get_json()

    if not data:
        return jsonify(response), 400

    fluent_resp = event.Event('follow', {
        'sender': data.get('sender'),
        'message': data.get('message'),
    })

    response['log'] = fluent_resp
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
