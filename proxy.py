from flask import Flask, request
from flask_restx import Api, Resource, fields
from datetime import datetime
from flask_cors import CORS
import requests

app = Flask(__name__)

CORS(app, origins=["https://get-dkan.ddev.site", "https://wren-liberal-optionally.ngrok-free.app"], supports_credentials=True)

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

api = Api(app, version='1.0', title='Open 311 API',
          description='City of Portland, Oregon',
          **swagger_ui_config)

ns = api.namespace('Services', description='')


#data models
service_list_model = api.model('Service List', {
  "jurisdiction_id": fields.String(required=True, description='Jurisdiction ID'),
  "service_code": fields.String(required=True, description='Service Code'),
  "service_name": fields.String(required=True, description='Service Name'),
  'description': fields.String(required=True, description='Description of the service'),
  "metadata": fields.String(required=True, description='Metadata flag'),
  "type": fields.String(required=True, description='Service type'),
  "keywords": fields.String(required=True, description='Service keywords'),
  "group": fields.String(required=True, description='Service group')
})


service_request_model = api.model('Service Request', {
  'service_request_id': fields.String(required=True, description='Service Request ID'),
  'status': fields.String(required=True, description='Status of the service request'),
  'service_name': fields.String(required=True, description='Name of the service'),
  'service_code': fields.String(required=True, description='Service Code'),
  'description': fields.String(required=True, description='Description of the service request'),
  'agency_responsible': fields.String(required=True, description='Responsible agency'),
  'requested_datetime': fields.DateTime(required=True, description='Date and time of request'),
  'updated_datetime': fields.DateTime(required=True, description='Date and time of last update'),
  'address': fields.String(required=False, allow_none=True, description='Address of the service request'),
  'address_id': fields.String(required=False, description='Address ID'),
  'zipcode': fields.String(required=False, allow_none=True, description='Zip code of the location'),
  'lat': fields.String(required=False, allow_none=True, description='Latitude of the location'),
  'long': fields.String(required=False, allow_none=True, description='Longitude of the location'),
  'media_url': fields.String(required=False, allow_none=True, description='Media URL associated with the request'),
  'agency_id': fields.String(required=True, description='Agency ID'),
  'other_fields': fields.Raw(required=False, description='Additional fields including permit dates')
})


service_definition_model = api.model('Service Definition', {
  'service_code': fields.String(required=True, description='Unique identifier of the service'),
  'variable': fields.Boolean(required=True, description='Whether the field is variable'),
  'code': fields.String(required=True, description='The field code'),
  'datatype': fields.String(required=True, description='The data type of the field'),
  'required': fields.Boolean(required=True, description='Whether the field is required'),
  'datatype_description': fields.String(required=False, description='Additional description of the data type'),
  'order': fields.Integer(required=True, description='Display order of the field'),
  'description': fields.String(required=True, description='Description of the field')
})


error_model = api.model('Error', {
  'message': fields.String(required=True, description='Error message')
})

def retrieveData(bucket, tag):
  url_identifier = "https://get-dkan.ddev.site/api/1/search"
  ca = "/mnt/ddev-global-cache/mkcert/rootCA.pem"
  params = {
    'keyword': tag
  }
  response = requests.get(url_identifier, params=params, verify=ca)
  data_identifiers = response.json()

  # Iterate over each dataset in the "results"
  for dataset_key, dataset_value in data_identifiers.get("results").items():
    ref_distributions = dataset_value.get("%Ref:distribution")
    for distribution in ref_distributions:
      loadAll = False
      resource_id = distribution['identifier']
      offset = 0
      while not loadAll:
        url_dataset = f"https://get-dkan.ddev.site/api/1/datastore/query/{resource_id}?offset={offset}"
        json_response = requests.get(url_dataset, verify=ca).json()
        limit = json_response['count']
        entries = json_response['results']
        if (tag == 'Request'):
          date_format = '%Y-%m-%d %H:%M:%S'
          for entry in entries:
            entry['requested_datetime'] = datetime.strptime(entry['requested_datetime'], date_format)
            entry['updated_datetime'] = datetime.strptime(entry['updated_datetime'], date_format)
            bucket.append(entry)
        else:
          for entry in entries:
            bucket.append(entry)
        offset += len(entries)
        loadAll = offset == limit

@ns.route('/service_list')
class ServiceList(Resource):
  @ns.doc('service_list')
  @ns.marshal_list_with(service_list_model)
  @ns.response(200, 'Success')
  @ns.response(400, 'Bad Request', error_model)
  @ns.response(404, 'No Services Found', error_model)
  @ns.response(500, 'Internal Server Error', error_model)
  @ns.param('jurisdiction_id', 'Filter by jurisdiction ID')
  @ns.param('service_code', 'Filter by service code')
  @ns.param('service_name', 'Filter by service name (case-insensitive)')
  @ns.param('description', 'Filter by description (case-insensitive partial match)')
  @ns.param('metadata', 'Filter by metadata (TRUE/FALSE)')
  @ns.param('type', 'Filter by service type')
  @ns.param('keywords', 'Filter by keywords (comma-separated)')
  @ns.param('group', 'Filter by group')
  def get(self):
    """
    Get service list with optional filters

    This endpoint allows you to retrieve a list of available services. You can apply filters to narrow down the results.
    All text filters are case-insensitive. Keywords filter supports comma-separated values for multiple keyword search.
    """
    try:
      service_list = []
      retrieveData(service_list, 'Service')
      filtered_services = service_list

      # Filter by jurisdiction_id
      if request.args.get('jurisdiction_id'):
        filtered_services = [service for service in filtered_services if service['jurisdiction_id'].lower() == request.args.get('jurisdiction_id').lower()]

      # Filter by service_code
      if request.args.get('service_code'):
        filtered_services = [service for service in filtered_services if service['service_code'].lower() == request.args.get('service_code').lower()]

      # Filter by service_name (case-insensitive)
      if request.args.get('service_name'):
        filtered_services = [service for service in filtered_services if request.args.get('service_name').lower() in service['service_name'].lower()]

      # Filter by description (partial match, case-insensitive)
      if request.args.get('description'):
        filtered_services = [service for service in filtered_services if request.args.get('description').lower() in service['description'].lower()]

      # Filter by metadata
      if request.args.get('metadata'):
        filtered_services = [service for service in filtered_services if str(service['metadata']).upper() == request.args.get('metadata').upper()]

      # Filter by type
      if request.args.get('type'):
        filtered_services = [service for service in filtered_services if service['type'].lower() == request.args.get('type').lower()]

      # Filter by keywords (supports multiple keywords)
      if request.args.get('keywords'):
        search_keywords = [k.strip().lower() for k in request.args.get('keywords').split(',')]
        filtered_services = [service for service in filtered_services if any(keyword in service['keywords'].lower() for keyword in search_keywords)]

      # Filter by group
      if request.args.get('group'):
        filtered_services = [service for service in filtered_services if service['group'].lower() == request.args.get('group').lower()]

      if not filtered_services:
        return {'message': 'No services found matching the criteria.'}, 404

      return filtered_services, 200

    except Exception as e:
      return {'message': f'An unexpected error occurred: {str(e)}'}, 500


@ns.route('/service_requests')
class ServiceRequest(Resource):
  @ns.doc('service_requests')
  @ns.marshal_list_with(service_request_model)
  @ns.response(200, 'Success')
  @ns.response(400, 'Bad Request', error_model)
  @ns.response(404, 'No Service Requests Found', error_model)
  @ns.response(500, 'Internal Server Error', error_model)
  @ns.param('service_request_id', 'Filter by service request ID')
  @ns.param('status', 'Filter by status')
  @ns.param('service_code', 'Filter by service code')
  @ns.param('service_name', 'Filter by service name')
  @ns.param('agency_responsible', 'Filter by responsible agency')
  @ns.param('start_date', 'Start date for time range filter (YYYY-MM-DD)')
  @ns.param('end_date', 'End date for time range filter (YYYY-MM-DD)')
  @ns.param('address_id', 'Filter by address ID')
  @ns.param('zipcode', 'Filter by zipcode')
  @ns.param('agency_id', 'Filter by agency ID')
  @ns.param('lat', 'Filter by latitude')
  @ns.param('long', 'Filter by longitude')
  @ns.param('updated_start_date', 'Start date for last update filter (YYYY-MM-DD)')
  @ns.param('updated_end_date', 'End date for last update filter (YYYY-MM-DD)')
  def get(self):
    """
    Get all service requests with optional filters

    This endpoint allows you to retrieve a list of service requests. You can apply various filters to narrow down the results.
    """
    try:
      service_requests = []
      retrieveData(service_requests, 'Request')
      filtered_requests = service_requests

      # Basic string filters
      string_filters = [
        'service_request_id', 'status', 'service_code', 'service_name',
        'agency_responsible', 'address_id', 'zipcode', 'agency_id'
      ]
      for filter_name in string_filters:
        if request.args.get(filter_name):
          filtered_requests = [
            req for req in filtered_requests
            if req[filter_name] == request.args.get(filter_name)
          ]

      # Coordinate filters
      if request.args.get('lat'):
        try:
          lat = str(request.args.get('lat'))
          filtered_requests = [req for req in filtered_requests if req['lat'] == lat]
        except ValueError:
          return {'message': 'Invalid latitude format.'}, 400

      if request.args.get('long'):
        try:
          long = str(request.args.get('long'))
          filtered_requests = [req for req in filtered_requests if req['long'] == long]
        except ValueError:
          return {'message': 'Invalid longitude format.'}, 400

      # Request date range filter
      start_date = request.args.get('start_date')
      end_date = request.args.get('end_date')
      if start_date and end_date:
        try:
          start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
          end_datetime = datetime.strptime(end_date, '%Y-%m-%d').replace(
            hour=23, minute=59, second=59
          )
          filtered_requests = [
            req for req in filtered_requests
            if start_datetime <= req['requested_datetime'] <= end_datetime
          ]
        except ValueError:
          return {'message': 'Invalid date format. Please use YYYY-MM-DD.'}, 400

      # Update date range filter
      updated_start_date = request.args.get('updated_start_date')
      updated_end_date = request.args.get('updated_end_date')
      if updated_start_date and updated_end_date:
        try:
          updated_start_datetime = datetime.strptime(updated_start_date, '%Y-%m-%d')
          updated_end_datetime = datetime.strptime(updated_end_date, '%Y-%m-%d').replace(
            hour=23, minute=59, second=59
          )
          filtered_requests = [
            req for req in filtered_requests
            if updated_start_datetime <= req['updated_datetime'] <= updated_end_datetime
          ]
        except ValueError:
          return {'message': 'Invalid date format for update date range. Please use YYYY-MM-DD.'}, 400

      if not filtered_requests:
        return {'message': 'No service requests found matching the criteria.'}, 404

      return filtered_requests, 200

    except Exception as e:
      return {'message': f'An unexpected error occurred: {str(e)}'}, 500


@ns.route('/service_definition')
class ServiceDefinition(Resource):
  @ns.doc('service_definition')
  @ns.marshal_list_with(service_definition_model)
  @ns.response(200, 'Success')
  @ns.response(400, 'Bad Request', error_model)
  @ns.response(404, 'No Definitions Found', error_model)
  @ns.response(500, 'Internal Server Error', error_model)
  @ns.param('service_code', 'Filter by service code (case-insensitive)')
  @ns.param('variable', 'Filter by variable status (TRUE/FALSE)')
  @ns.param('code', 'Filter by field code (case-insensitive)')
  @ns.param('datatype', 'Filter by data type (case-insensitive)')
  @ns.param('required', 'Filter by required status (TRUE/FALSE)')
  @ns.param('datatype_description', 'Filter by datatype description (case-insensitive partial match)')
  @ns.param('order', 'Filter by order number')
  @ns.param('description', 'Filter by description (case-insensitive partial match)')
  def get(self):
    """
    Get service definition fields with optional filters

    This endpoint allows you to retrieve service definitions for a specific service code. You can apply filters to narrow down the results.
    All text filters are case-insensitive. Boolean filters accept TRUE/FALSE values.
    """
    try:
      service_definitions = []
      retrieveData(service_definitions, 'Definition')
      filtered_definitions = service_definitions

      # Filter by service_code
      if request.args.get('service_code'):
        filtered_definitions = [definition for definition in filtered_definitions if definition['service_code'].lower() == request.args.get('service_code').lower()]

      # Filter by variable
      if request.args.get('variable'):
        variable_value = request.args.get('variable').upper()
        filtered_definitions = [definition for definition in filtered_definitions if definition['variable'].upper() == variable_value]

      # Filter by code
      if request.args.get('code'):
        filtered_definitions = [definition for definition in filtered_definitions if definition['code'].lower() == request.args.get('code').lower()]

      # Filter by datatype
      if request.args.get('datatype'):
        filtered_definitions = [definition for definition in filtered_definitions if definition['datatype'].lower() == request.args.get('datatype').lower()]

      # Filter by required
      if request.args.get('required'):
        required_value = request.args.get('required').upper()
        filtered_definitions = [definition for definition in filtered_definitions
                                if definition['required'].upper() == required_value]

      # Filter by datatype_description
      if request.args.get('datatype_description'):
        search_term = request.args.get('datatype_description').lower()
        filtered_definitions = [definition for definition in filtered_definitions if definition.get('datatype_description') and search_term in definition['datatype_description'].lower()]

      # Filter by order
      if request.args.get('order'):
        order_value = request.args.get('order')
        filtered_definitions = [definition for definition in filtered_definitions if definition['order'] == order_value]

      # Filter by description
      if request.args.get('description'):
        search_term = request.args.get('description').lower()
        filtered_definitions = [definition for definition in filtered_definitions if search_term in definition['description'].lower()]

      if not filtered_definitions:
        return {'message': 'No definitions found matching the criteria.'}, 404

      return filtered_definitions, 200

    except ValueError as e:
      return {'message': 'Invalid parameter value provided.'}, 400
    except Exception as e:
      return {'message': f'An unexpected error occurred: {str(e)}'}, 500

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
  # app.run(host='0.0.0.0', port=5000, ssl_context=('127.0.0.1+1.pem', '127.0.0.1+1-key.pem'))
