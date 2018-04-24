import pandas as pd 
from api.models import MusicResource, TextResource, MusicRecord

def parse_library(library_file, organization_id):
    df = pd.read_excel(library_file, 'Sheet1', index_col=None)
    for index,row in df.iterrows():
        if(row['TITLE']!=None):
            try:
                mrecord, created = MusicRecord.objects.get_or_create(organization_id= organization_id, title= row['TITLE'],composer=row['COMPOSER'], publisher=row['PUBLISHER'], arranger=row['ARRANGER'], instrumentation=row['INSTRUMENTATION'])
                mrecord.save()
                text_resource, created = TextResource.objects.get_or_create(title = row['TITLE'], music_record = mrecord, type='youtube_link', field=row['YOUTUBE LINK'], description=None)
                text_resource.save()
            except: 
                return False
    return True
