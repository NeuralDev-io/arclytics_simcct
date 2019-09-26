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


__status__ = 'development'
__date__ = '2019.08.28'
"""app.py: 

This module is a very basic Flask application with a single endpoint to send 
an Event emitted log to the fluentd microservice.
"""

import os

from fluent import sender, event
from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)

CORS(app)

fluent_host = os.environ.get('FLUENT_HOST')
sender.setup('fluent-python', host=fluent_host, port=24224)


@app.route('/log', methods=['POST'])
def log():
    response = {'status': 'fail'}

    data = request.get_json()

    if not data:
        return jsonify(response), 400

    # Hostname of the running container is the Docker ID (short)
    container_id = os.environ.get('HOSTNAME')

    # Emit the event to the fluentd microservice
    event.Event('debug', {
        'log': data['message'],
        'container_name': '/arc_fluent_python_1',
        'container_id': container_id,
        'source': 'python'
    })

    # Also sending the response back to check that it worked properly.
    response['log'] = data['message']
    response['container_id'] = container_id
    response['status'] = 'success'
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
