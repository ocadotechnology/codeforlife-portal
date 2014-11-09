# -*- coding: utf-8 -*-
from django.db import models, migrations
from datetime import datetime

def insert_news(apps, schema_editor):
    FrontPageNews = apps.get_model('portal', 'FrontPageNews')

    news1 = FrontPageNews.objects.create(
        title="Teachers 'not confident on coding'",
        text="Computer coding is being introduced to the school curriculum in less than six weeks' time, but many primary school teachers will be under-prepared to teach the new subject, according to a new poll.",
        link="http://www.dailymail.co.uk/wires/pa/article-2700124/TEACHERS-NOT-CONFIDENT-ON-CODING.html?ITO=1490&ns_mchannel=rss&ns_campaign=1490",
        link_text='Read more on www.dailymail.co.uk',
        added_dstamp=datetime.now())
    news2 = FrontPageNews.objects.create(
        title="British schools are not prepared to teach coding",
        text="With just six weeks until the new computing curriculum is introduced in UK schools, research has revealed that British primary school teachers are not fully prepared to teach their pupils how to code.",
        link="http://www.cbronline.com/news/social/british-teachers-are-not-prepared-to-teach-coding-4322259",
        link_text="Read more on www.cbronline.co.uk",
        added_dstamp=datetime.now())
    news3 = FrontPageNews.objects.create(
        title="Ocado launches free Code For Life tool to help 130,000 apprehensive primary school teachers",
        text="Thousands of primary school teachers aren’t ready to teach computer coding lessons that become part of the country’s national curriculum for computing before the start of the academic year in September.",
        link="http://www.itproportal.com/2014/07/21/ocado-launches-free-code-life-tool-help-130000-apprehensive-primary-school-teachers/?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+itproportal%2Frss+(Latest+ITProPortal+News)",
        link_text="Read more on itproportal.com",
        added_dstamp=datetime.now())
    news4 = FrontPageNews.objects.create(
        title="Ocado Technology launches coding resources for teachers",
        text="Ocado Technology is the latest business to get involved with preparing teachers for the new computing curriculum that comes into effect in September",
        link="http://www.computerworlduk.com/news/careers/3531070/ocado-technology-launches-coding-resources-for-teachers/",
        link_text="Read more on www.computerworlduk.com",
        added_dstamp=datetime.now())
    news5 = FrontPageNews.objects.create(
        title="Not Enough Teachers Will Know Code By September",
        text="A new curriculum brings coding into primary schools in September – and it looks as if teachers won’t be able to cope. ",
        link="http://www.techweekeurope.co.uk/news/not-enough-teachers-know-code-149462",
        link_text="Read more on www.techweekeurope.co.uk",
        added_dstamp=datetime.now())
    news6 = FrontPageNews.objects.create(
        title="Ocado Technology readies primary school teachers with code initiative",
        text="Ocado Technology has launched a coding initiative after finding that 73% of primary school teachers feel they have not been given the necessary resources to teach children to code.",
        link="http://www.computerweekly.com/news/2240225117/Ocado-Technology-readies-primary-school-teachers-with-code-initiative",
        link_text="Read more on www.computerweekly.com",
        added_dstamp=datetime.now())
    news7 = FrontPageNews.objects.create(
        title="Curriculum countdown",
        text="According to new research more than 130,000 primary school teachers don’t feel confident enough to teach computer coding",
        link="http://edtechnology.co.uk/Featured-Content/curriculum_countdown",
        link_text="Read more on www.edtechnology.co.uk",
        added_dstamp=datetime.now())
    news8 = FrontPageNews.objects.create(
        title="Computing Curriculum Countdown: Over 130,000 Primary School Teachers Don’t Feel Confident Enough to Teach Computer Coding",
        text="Many primary school teachers feel they haven’t been given the necessary resources to teach the new Computing curriculum from September. ",
        link="http://www.primarytimes.net/news/2014/07/computing-curriculum-countdown-over-130-000-primary-school-teachers-don-t-feel-confident-enough-to-teach-computer-coding-",
        link_text="Read more on www.primarytimes.net",
        added_dstamp=datetime.now())
    news9 = FrontPageNews.objects.create(
        title="Ocado’s technology team to release primary school coding tool",
        text="Ocado’s technology team is launching Code for Life, the online grocer’s initiative to help children learn to code.",
        link="http://internetretailing.net/2014/07/ocados-technology-team-launch-primary-school-coding-tool/",
        link_text="Read more on www.internetretailing.net",
        added_dstamp=datetime.now())
    news10 = FrontPageNews.objects.create(
        title="Teachers 'not confident' over coding",
        text="Computer coding is being introduced to the school curriculum in less than six weeks' time, but many primary school teachers will be under-prepared to teach the new subject, according to a new poll.",
        link="http://www.dailyecho.co.uk/leisure/technology/11358091.Teachers__not_confident__over_coding/",
        link_text="Read more on www.dailyecho.co.uk",
        added_dstamp=datetime.now())
    news11 = FrontPageNews.objects.create(
        title="Ocado Technology launches coding resources for teachers",
        text="Ocado Technology is a latest business to get concerned with scheming teachers for a new computing curriculum that comes into outcome in September.",
        link="http://www.datacentremanagement.org/2014/07/ocado-technology-launches-coding-resources-for-teachers/",
        link_text="Read more on www.datacentremanagement.org",
        added_dstamp=datetime.now())
    news12 = FrontPageNews.objects.create(
        title="Teachers 'not confident enough' to teach code",
        text="More than 70% of primary school teachers say they don't feel confident enough to teach the new coding syllabus being introduced this September.",
        link="http://www.newelectronics.co.uk/electronics-news/teachers-not-confident-enough-to-teach-code/62697/",
        link_text="Read more on www.newelectronics.co.uk",
        added_dstamp=datetime.now())

class Migration(migrations.Migration):
    dependencies = [
            ('portal', '0038_frontpagenews'),
    ]

    operations = [
            migrations.RunPython(insert_news),
    ]
