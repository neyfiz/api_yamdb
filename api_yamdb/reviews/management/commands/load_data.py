import csv
from django.core.management.base import BaseCommand

from reviews.models import (
    Category,
    Comment,
    Genre,
    GenreTitle,
    Review,
    Title,
    User
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        models = [
            (User, 'users.csv', {
                'id': 'id',
                'username': 'username',
                'email': 'email',
                'role': 'role',
                'bio': 'bio',
                'first_name': 'first_name',
                'last_name': 'last_name',
            }),
            (Category, 'category.csv', {
                'id': 'id',
                'name': 'name',
                'slug': 'slug',
            }),
            (Genre, 'genre.csv', {
                'id': 'id',
                'name': 'name',
                'slug': 'slug',
            }),
            (Title, 'titles.csv', {
                'id': 'id',
                'name': 'name',
                'year': 'year',
                'category_id': 'category',
            }),
            (GenreTitle, 'genre_title.csv', {
                'id': 'id',
                'title_id': 'title_id',
                'genre_id': 'genre_id',
            }),
            (Review, 'review.csv', {
                'id': 'id',
                'title_id': 'title_id',
                'text': 'text',
                'author_id': 'author',
                'score': 'score',
                'pub_date': 'pub_date',
            }),
            (Comment, 'comments.csv', {
                'id': 'id',
                'review_id': 'review_id',
                'text': 'text',
                'author_id': 'author',
                'pub_date': 'pub_date',
            }),
        ]

        for model, filename, fields in models:
            self.import_data(model, filename, fields)

    def import_data(self, model, filename, fields):
        with open(f'static/data/{filename}', 'r', encoding='utf-8') as csvfile:
            dict_reader = csv.DictReader(csvfile)
            for row in dict_reader:
                obj, created = model.objects.get_or_create(
                    **{field: row[value] for field, value in fields.items()}
                )
