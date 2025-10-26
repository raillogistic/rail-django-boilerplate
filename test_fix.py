import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from graphene.test import Client
from config.schema import schema

client = Client(schema)

query = '''
{
   model_form_metadata(app_name:"blog",model_name:"Post"){
     required_permissions
     relationships{
       name
       related_model
     }
   }
}
'''

result = client.execute(query)
print('Query result:')
print(result)