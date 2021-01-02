import sys
from marshmallow import ValidationError
from flask import Flask, jsonify, request
from flask_restful import abort, Api, Resource
from flask_cors import CORS
from main_solver import solve, InputSchema

app = Flask(__name__)
CORS(app)
api = Api(app)

class Optimize(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        # this is horrible but I can't get reqparse to cooperate
        validator = InputSchema()
        try:
            parsed = validator.load(json_data)
            if parsed['leniency'] > parsed['transform_time']:
                raise ValidationError("leniency exceeds transformation duration")
        except ValidationError as e:
            return 'error: {}'.format(str(e)), 400
        print(parsed)
        solution = solve(parsed, output=False)
        print(solution)
        return solution, 200

api.add_resource(Optimize, '/api/optimize')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
