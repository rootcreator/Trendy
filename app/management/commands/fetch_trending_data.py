from django.core.management.base import BaseCommand
from app.views import fetch_trending_data
from app.models import Trend


class Command(BaseCommand):
    help = 'Fetch and update trending data'

    def handle(self, *args, **kwargs):
        data = fetch_trending_data()

        for source, trends in data.items():
            for item in trends:
                title = item.get('title') or item.get('name') or item.get('id')
                description = item.get('description') or ''
                url = item.get('url') or ''
                Trend.objects.update_or_create(
                    title=title,
                    defaults={'description': description, 'url': url, 'source': source}
                )

        self.stdout.write(self.style.SUCCESS('Successfully updated trends'))
