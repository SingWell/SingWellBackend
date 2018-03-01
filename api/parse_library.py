import pandas as pd 
from api.models import MusicResource, TextResource, MusicRecord

def parse_library(library_file, organization_id):
    df = pd.read_excel(library_file, 'Sheet1', index_col=None)
    for index,row in df.iterrows():
        if(row['TITLE']!=None):
            mrecord, created = MusicRecord.objects.get_or_create(organization_id= organization_id, title= row['TITLE'],composer=row['COMPOSER'], publisher=row['PUBLISHER'], instrumentation=row['SCORING'])
            mrecord.save()
    return True
