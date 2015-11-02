from keystoneclient.auth.identity import v2
from keystoneclient import session
from novaclient import client

AUTH_URL = 'http://11.11.1.204:5000/v2.0/'
USERNAME = 'admin'
PASSWORD = 'admin'
PROJECT_ID = 'admin'

auth = v2.Password(auth_url=AUTH_URL,
                   username=USERNAME,
                   password=PASSWORD,
                   tenant_name=PROJECT_ID)

print auth.token
sess = session.Session(auth=auth)
nova = client.Client('1.1', session=sess)

hypervisors =  nova.hypervisors.list()

print hypervisors
print hypervisors[0].host_ip
print hypervisors[1].host_ip
print hypervisors[2].host_ip
