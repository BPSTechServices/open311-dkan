from flask import Flask, request
from flask_restx import Api, Resource, fields
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "https://get-dkan.ddev.site"}})

# Swagger UI Config
swagger_ui_config = {
  'swagger_ui_config': {
    'docExpansion': 'list',
    'defaultModelsExpandDepth': -1,
    'displayRequestDuration': True,
    'syntaxHighlight': {
      'theme': 'monokai'
    },
    'deepLinking': True,
    'displayOperationId': True,
    'filter': True,
  },
  'swagger_ui_css': [
    'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.43.0/swagger-ui.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.43.0/swagger-ui-standalone-preset.min.css'
  ],
  'swagger_ui_bundle_js': 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.43.0/swagger-ui-bundle.min.js',
  'swagger_ui_standalone_preset_js': 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.43.0/swagger-ui-standalone-preset.min.js',
}

api = Api(app, version='1.0', title='Cases API',
          description='City of Portland, Oregon',
          **swagger_ui_config)

ns = api.namespace('cases', description='Cases operations')

case_model = api.model('Case', {
  'service_request_id': fields.String(required=True, description='Service Request ID'),
  'status': fields.String(required=True, description='Status of the case'),
  'service_code': fields.String(required=True, description='Service Code'),
  'description': fields.String(required=True, description='Description of the case'),
  'requested_datetime': fields.DateTime(required=True, description='Date and time of request'),
  'updated_datetime': fields.DateTime(required=True, description='Date and time of last update'),
  'agency_responsible': fields.String(required=True, description='Responsible agency'),
  'agency_id': fields.String(required=True, description='Agency ID'),
  'location': fields.String(required=True, description='Location of the case')
})

error_model = api.model('Error', {
  'message': fields.String(required=True, description='Error message')
})


# Dummy Data
cases = [
  {
    'service_request_id': '20274',
    'status': 'closed',
    'service_code': 'report_trash_can',
    'description': 'Trash can report: Other',
    'requested_datetime': datetime(2022, 11, 13, 10, 49),
    'updated_datetime': datetime(2022, 11, 21, 9, 1),
    'agency_responsible': 'BPS: Public Trash',
    'agency_id': '9153139263895',
    'Census block': '2025'
  },
  {
    'service_request_id': '21384',
    'status': 'closed',
    'service_code': 'report_trash_can',
    'description': 'Trash can report: Other',
    'requested_datetime': datetime(2022, 11, 23, 16, 7),
    'updated_datetime': datetime(2022, 12, 5, 9, 1),
    'agency_responsible': 'BPS: Public Trash',
    'agency_id': '9153139263895',
    'Census block': '4033'
  }
]


@ns.route('/')
class CaseList(Resource):
  @ns.doc('list_cases')
  @ns.marshal_list_with(case_model)
  @ns.response(200, 'Success')
  @ns.response(400, 'Bad Request', error_model)
  @ns.response(404, 'No Cases Found', error_model)
  @ns.response(500, 'Internal Server Error', error_model)
  @ns.param('service_request_id', 'Filter by service request ID')
  @ns.param('status', 'Filter by status')
  @ns.param('service_code', 'Filter by service code')
  @ns.param('start_date', 'Start date for time range filter (YYYY-MM-DD)')
  @ns.param('end_date', 'End date for time range filter (YYYY-MM-DD)')
  def get(self):
    """
    List all cases with optional filters

    This endpoint allows you to retrieve a list of cases. You can apply various filters to narrow down the results.
    """
    try:
      filtered_cases = cases

      # Apply filters based on query parameters
      if request.args.get('service_request_id'):
        filtered_cases = [case for case in filtered_cases if case['service_request_id'] == request.args.get('service_request_id')]
      if request.args.get('status'):
        filtered_cases = [case for case in filtered_cases if case['status'] == request.args.get('status')]
      if request.args.get('service_code'):
        filtered_cases = [case for case in filtered_cases if case['service_code'] == request.args.get('service_code')]

      # Apply time range filter
      start_date = request.args.get('start_date')
      end_date = request.args.get('end_date')
      if start_date and end_date:
        try:
          start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
          end_datetime = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
          filtered_cases = [case for case in filtered_cases if start_datetime <= case['requested_datetime'] <= end_datetime]
        except ValueError:
          return {'message': 'Invalid date format. Please use YYYY-MM-DD.'}, 400

      if not filtered_cases:
        return {'message': 'No cases found matching the criteria.'}, 404

      return filtered_cases, 200

    except Exception as e:
      return {'message': f'An unexpected error occurred: {str(e)}'}, 500


@ns.route('/<string:service_request_id>')
class Case(Resource):
  @ns.doc('get_case')
  @ns.marshal_with(case_model)
  @ns.response(200, 'Success')
  @ns.response(404, 'Case Not Found', error_model)
  @ns.response(500, 'Internal Server Error', error_model)
  def get(self, service_request_id):
    """
    Get a specific case by service request ID

    This endpoint retrieves a single case based on the provided service request ID.
    """
    try:
      case = next((case for case in cases if case['service_request_id'] == service_request_id), None)
      if case:
        return case, 200
      else:
        return {'message': 'Case not found'}, 404
    except Exception as e:
      return {'message': f'An unexpected error occurred: {str(e)}'}, 500


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
