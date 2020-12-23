import sys
from flask import Flask, jsonify, request
from flask_restful import abort, Api, Resource
from main_solver import solve, check_input

app = Flask(__name__)
api = Api(app)

class Optimize(Resource):
    def post(self):
        # print('data recieved', file=sts.stderr)
        json_data = request.get_json(force=True)
        # this is horrible but I can't get reqparse to cooperate
        proceed = check_input(json_data)
        #print('data checked', file=sys.stderr)
        if proceed:
            #print('bonked', file=sys.stderr)
            return proceed, 400
        #print('no bonk', file=sys.stderr)
        solution = solve(json_data, output=False)
        print(solution)
        return solution, 200

api.add_resource(Optimize, '/api/optimize')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
