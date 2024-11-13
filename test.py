import requests
from datetime import datetime

from proxy import service_list


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
    resource_id = ref_distributions[0]['identifier']
    url_dataset = f"https://get-dkan.ddev.site/api/1/datastore/query/{resource_id}"
    response = requests.get(url_dataset, verify=ca)
    response = response.json()['results']
    if (tag == 'Request'):
      date_format = '%m/%d/%Y %H:%M'
      for item in response:
        item['requested_datetime'] = datetime.strptime(item['requested_datetime'], date_format)
        item['updated_datetime'] = datetime.strptime(item['updated_datetime'], date_format)
    bucket.append(response)

service_requests=[]
retrieveData(service_requests, 'Request')
print(service_requests)
