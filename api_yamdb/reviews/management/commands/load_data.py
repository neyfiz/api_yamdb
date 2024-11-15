import csv

from django.core.management import BaseCommand

from reviews.models import (
    Category, Comment, Genre, GenreTitle, Review, Title, User
)


class Command(BaseCommand):

    def handle(self, *args, **options):

        with open('static/data/users.csv', 'r', encoding='utf-8') as csvfile:
            dict_reader = csv.DictReader(csvfile)
            for row in dict_reader:
                User.objects.get_or_create(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row['bio'],
                    first_name=row['first_name'],
                    last_name=row['last_name'])

        with open('static/data/category.csv', 'r',
                  encoding='utf-8') as csvfile:
            dict_reader = csv.DictReader(csvfile)
            for row in dict_reader:
                Category.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug'])

        with open('static/data/genre.csv', 'r', encoding='utf-8') as csvfile:
            dict_reader = csv.DictReader(csvfile)
            for row in dict_reader:
                Genre.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug'])

        with open('static/data/titles.csv', 'r', encoding='utf-8') as csvfile:
            dict_reader = csv.DictReader(csvfile)
            for row in dict_reader:
                Title.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category_id=row['category'])

        with open('static/data/genre_title.csv') as csvfile:
            dict_reader = csv.DictReader(csvfile)
            for row in dict_reader:
                GenreTitle.objects.get_or_create(
                    id=row['id'],
                    title_id=row['title_id'],
                    genre_id=row['genre_id'],
                )

        with open('static/data/review.csv', 'r', encoding='utf-8') as csvfile:
            dict_reader = csv.DictReader(csvfile)
            for row in dict_reader:
                Review.objects.get_or_create(
                    id=row['id'],
                    title_id=row['title_id'],
                    text=row['text'],
                    author_id=row['author'],
                    score=row['score'],
                    pub_date=row['pub_date'])

        with open('static/data/comments.csv', 'r',
                  encoding='utf-8') as csvfile:
            dict_reader = csv.DictReader(csvfile)
            for row in dict_reader:
                Comment.objects.get_or_create(
                    id=row['id'],
                    review_id=row['review_id'],
                    text=row['text'],
                    author_id=row['author'],
                    pub_date=row['pub_date'])
