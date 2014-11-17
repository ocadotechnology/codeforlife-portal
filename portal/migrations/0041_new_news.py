# -*- coding: utf-8 -*-
from django.db import models, migrations
from datetime import datetime

def insert_news(apps, schema_editor):
    FrontPageNews = apps.get_model('portal', 'FrontPageNews')

    news1 = FrontPageNews.objects.create(
        title="Bletchley Park: From Code-Breaking to Kids Coding",
        text="The National Museum of Computer has opened its free Weekend Codability Project. This is part of the Code for Life initiative which aims to inspire the next generation of computer scientists.",
        link="http://www.idgconnect.com/blog-abstract/9056/bletchley-park-from-code-breaking-kids-coding",
        link_text='Read more on idgconnect.com',
        added_dstamp=datetime.now())
    news2 = FrontPageNews.objects.create(
        title="Giving kids Codability",
        text="Weekend Codability aims to empower young people by introducing them to programming computers. Children will be taught how to give instructions to computers, change existing instructions in programs and create their own programs.",
        link="http://edtechnology.co.uk/News/giving_kids_codability",
        link_text="Read more on edtechnology.co.uk",
        added_dstamp=datetime.now())
    news3 = FrontPageNews.objects.create(
        title="Try your hand at Bletchley Park codability project",
        text="Following the introduction of computing to England’s school curriculum last month, young people across the country are being invited to try their hand at programming computers in Block H, the world's first purpose-built computer centre, on Bletchley Park.",
        link="http://www.mkweb.co.uk/COMPUTERS-Try-hand-Bletchley-Park-codability/story-23860128-detail/story.html",
        link_text="Read more on mkweb.co.uk",
        added_dstamp=datetime.now())

class Migration(migrations.Migration):
    dependencies = [
            ('portal', '0040_initial_news'),
    ]

    operations = [
            migrations.RunPython(insert_news),
    ]
