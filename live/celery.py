from celery import shared_task
from datetime import datetime
from .models import Stream

@shared_task
def delete_expired_streams():
    now = datetime.now()
    streams_to_delete = Stream.objects.filter(is_active=True)
    
    for stream in streams_to_delete:
        if stream.get_auto_delete_time() <= now:
            stream.is_active = False  
            stream.end_time = now    
            stream.save()
