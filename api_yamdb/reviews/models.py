from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Review(models.Model):
    title = models.ForeignKey(Title)
    author = models.ForeignKey(User)
    text = models.TextField()
    score = models.IntegerField()
    pub_date = models.DateTimeField('Publication Date', auto_now_add=True)


class Comment(models.Model):
    review = models.ForeignKey(Review)
    author = models.ForeignKey(User)
    text = models.TextField()
    pub_date = models.DateTimeField('Publication Date', auto_now_add=True)
