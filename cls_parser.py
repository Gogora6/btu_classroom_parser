#!/usr/bin/env python3

from flask import Flask, jsonify
from utils.functions import connect, get_scores, messages, only_course_names
import json
import requests
import yaml

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False

post_login_url = "https://classroom.btu.edu.ge/ge/login/trylogin"

request_url = f"https://classroom.btu.edu.ge/ge/student/me/courses"


conf = yaml.load(open('conf/application.yml'))
username = conf['user']['email']
password = conf['user']['password']


payload = {'username': username, 'password': password}

@app.route('/scores', methods=['GET'])
def scores():
	try:
		soup = connect(post_login_url, payload, request_url)
		result = only_course_names(soup)

		scores = [{'score': v, 'course_name': k} for k,v in result.items() ]
		return jsonify(scores)
	except:
		return 'No information'


@app.route('/detailed_scores', methods=['GET'])
def detailed_scores():
	try:
		soup = connect(post_login_url, payload, request_url)
		result = get_scores(post_login_url, payload)

		scores = [{'course_info': v, 'course_name': k} for k,v in result.items() ]

		return jsonify(scores)
	except:
		return 'No information'


@app.route('/messages', methods=['GET'])
def messages_full():
	try:
		messages_data = messages(post_login_url, payload)

		messages_data = [{'id': k, 'content': v} for k,v in messages_data.items() ]
		return jsonify(messages_data)
	except:
		return 'No information'


if __name__ == '__main__':
    app.run(debug=True)
