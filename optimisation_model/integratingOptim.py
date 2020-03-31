import pandas  as pd
from myparking_api.models import Parking
import json

a = Parking.objects.all()[0:5]
b = list(a.values())  # json array form
# from df to json
df = pd.DataFrame(b)
json_array = json.loads(df.to_json(orient='records'))

# init clusters
def initClusters():
    print('hh')

