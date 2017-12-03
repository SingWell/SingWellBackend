from api.models import Organization, Choir
from django.contrib.auth.models import User

# admin_user = User.objects.create_user("kenton", "kenton@gmail.com", "password123", first_name="Kenton", last_name="Kravig")
org, created = Organization.objects.get_or_create(name="St. Mark's", address="1201 Alma Drive, Plano, Texas 75075",
                                  description="St. Mark the Evangelist Catholic Church", owner=admin_user,
                                  website_url = "https://stmarkplano.org/")
org.save()
print ("Saved organization and admin user")
choirs = []
choirs.append({"name":"Folk Choir", "meeting_day":7, "meeting_day_start_time":"7:45:00am"})
choirs.append({"name":"Traditional Choir", "meeting_day":3, "meeting_day_start_time":"7:30:00pm"})
choirs.append({"name":"Guitar Choir", "meeting_day":7, "meeting_day_start_time":"3:00:00pm"})
choirs.append({"name":"Spirit Choir", "meeting_day":7, "meeting_day_start_time":"4:30:00pm"})
added_choirs = []
for entry in choirs:
    choir = Choir.objects.get_or_create(name=entry['name'], meeting_day=entry['meeting_day'],
         meeting_day_start_hour=entry['meeting_day_start_time'], organization=org)
    added_choirs.append(choir)
    choir.save()
print ("Created choirs")
print (added_choirs)

index = 0 
with open('api/helper-scripts/user_mock_data.csv') as user_data:
    for line in user_data:
        username = line.split(',')[0]
        password = line.split(',')[1]
        email = line.split(',')[2]
        first_name = line.split(',')[3]
        last_name = line.split(',')[4]
        user = User.objects.create_user(username,email, password, first_name=first_name, last_name=last_name)
        added_choirs[index%len(added_choirs)].choristers.add(user)
        user.save()
        index+=1
