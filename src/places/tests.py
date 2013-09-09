from django.contrib.auth.models import User
from django.http import response
from django.test import TestCase
from django.test.client import Client
from places.models import Place, Placemark, Vote


class PlacesTest(TestCase):
    def setUp(self):
        User.objects.create_user("segalle", email=None, password="1234")

        p = Place()
        p.vendor_id = 1000
        p.data = {
        "city": "\u05d9\u05e8\u05d5\u05e9\u05dc\u05d9\u05dd", 
        "name": "\u05e9\u05d9\u05da \u05d2'\u05e8\u05d0\u05d7", 
        "district": "\u05d9\u05e8\u05d5\u05e9\u05dc\u05d9\u05dd", 
        "phones": "02-5871923", 
        "notes": "", 
        "subdistrict": "\u05d9\u05e8\u05d5\u05e9\u05dc\u05d9\u05dd", 
        "days": [
            "8:00-17:00", 
            "8:00-17:00", 
            "8:00-17:00", 
            "8:00-17:00", 
            "8:00-13:00", 
            "\u05e1\u05d2\u05d5\u05e8"
        ], 
        "address": "\u05de\u05e8\u05db\u05d6 \u05e8\u05e4\u05d5\u05d0\u05d9", 
        "owner": "\u05e2\u05d9\u05e8\u05d9\u05d9\u05ea \u05d9\u05e8\u05d5\u05e9\u05dc\u05d9\u05dd", 
        "id": 1000
        }
        p.save()
        
        self.pm = Placemark()
        self.pm.place = p
        self.pm.city = "\u05d9\u05e8\u05d5\u05e9\u05dc\u05d9\u05dd"
        self.pm.address = "\u05de\u05e8\u05db\u05d6 \u05e8\u05e4\u05d5\u05d0\u05d9"
        self.pm.lat = 31.15
        self.pm.lng = 32.16
        self.pm.save()

        self.pm1 = Placemark()
        self.pm1.place = p
        self.pm1.city = "\u05d9\u05e8\u05d5\u05e9\u05dc\u05d9\u05dd"
        self.pm1.address = "\u05de\u05e8\u05db\u05d6 \u05e8\u05e4\u05d5\u05d0\u05d9"
        self.pm1.lat = 31.25
        self.pm1.lng = 32.26
        self.pm1.save()

        self.pm2 = Placemark()
        self.pm2.place = p
        self.pm2.city = "\u05d9\u05e8\u05d5\u05e9\u05dc\u05d9\u05dd"
        self.pm2.address = "\u05de\u05e8\u05db\u05d6 \u05e8\u05e4\u05d5\u05d0\u05d9"
        self.pm2.lat = 31.35
        self.pm2.lng = 32.36
        self.pm2.save()

    def test_votes(self):
        c = Client()
        c.login(username="segalle", password="1234")
        response = c.post('/vote/', {'id': str(self.pm.id), 'positive': 'True'})
        self.assertEqual(response.content, "OK")

    def test_login(self):
        c = Client()
        response = c.post('/vote/', {'id': str(self.pm.id), 'positive': 'True'})
        self.assertRedirects(response, '/login/?next=/vote/')

    def test_double_entry(self):
        c = Client()
        c.login(username="segalle", password="1234")
        response = c.post('/vote/', {'id': str(self.pm1.id), 'positive': 'True'})
        response1 = c.post('/vote/', {'id': str(self.pm1.id), 'positive': 'True'})

        self.assertEqual(response.content, "OK")
        self.assertEqual(response1.content, "exists")
        
    def test_request_method(self):
        c = Client()
        c.login(username="segalle", password="1234")
        response = c.post('/vote/', {'id': str(self.pm1.id), 'positive': 'True'})
        response1 = c.get('/vote/', {'id': str(self.pm1.id), 'positive': 'True'})
        
        self.assertEqual(response.content, "OK")
        self.assertEqual(response1.content, "Wrong request method")
        
    
    def test_addplacemark(self):
        c = Client()
        c.login(username="segalle", password="1234")
        response = c.post('/addplacemark/', {
                            'place': self.pm.place.id,
                            'address': self.pm.address,
                            'city': self.pm.city,
                            'lat': self.pm.lat,
                            'lng': self.pm.lng
                            })
        self.assertEqual(response.content, "exists")
        response1= c.post('/addplacemark/', {
                            'place': self.pm.place.id,
                            'address': self.pm.address,
                            'city': u'Tel Aviv',
                            'lat': self.pm.lat,
                            'lng': self.pm.lng
                            })
        
        self.assertEqual(response1.content, "OK")
        response2= c.post('/addplacemark/', {
                            'place': self.pm.place.id,
                            'address': self.pm.address,
                            'city': u'Tel Aviv',
                            'lat': self.pm.lat,
                            'lng': self.pm.lng
                            })
        
        self.assertEqual(response2.content, "exists")
        response3= c.post('/addplacemark/', {
                            'place': 99999,
                            'address': self.pm.address,
                            'city': u'Tel Aviv',
                            'lat': self.pm.lat,
                            'lng': self.pm.lng
                            })
        
        self.assertEqual(response3.content, "OK")