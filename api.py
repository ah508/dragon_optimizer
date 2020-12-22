from flask import Flask, jsonify, request
from flask_restful import abort, Api, Resource
from main_solver import solve, check_input
from flask_jwt import JWT

app = Flask(__name__)
api = Api(app)

class Optimize(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        # this is horrible but I can't get reqparse to cooperate
        proceed = check_input(json_data)
        if proceed:
            return proceed, 400
        solution = solve(json_data, output=False)
        return solution, 200

api.add_resource(Optimize, '/api/optimize')

if __name__ == "__main__":
    app.run(debug=True)