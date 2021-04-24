from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
import datetime

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)
    genre = models.CharField(max_length=200)
    summary = models.CharField(max_length=2000)
    ISBN = models.BigIntegerField()
    location = models.CharField(max_length=200)
    available = models.BooleanField()
    cover = models.FileField()

    def __str__(self):
        return self.title

class Request(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    start_date = models.DateField(default=datetime.date.today)
    end_date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(2)])   # 0 Waiting, 1 Accepted, 2 Declined
    
    def __str__(self):
        return self.user.username + '-' + self.book.title

    def is_ongoing(self):
        if datetime.date.today() <= self.end_date and datetime.date.today() >= self.start_date:
            return True
        return False
    
    def number_of_days(self):
        num = self.end_date - datetime.date.today()
        return num.days

    def is_deadline_close(self):
        if(self.number_of_days()<=2):
            return True
        return False