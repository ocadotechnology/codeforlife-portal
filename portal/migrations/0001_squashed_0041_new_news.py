# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2019, Ocado Innovation Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

from django.contrib.auth.hashers import make_password
from django.utils import timezone
import os

# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
# portal.migrations.0001_squashed_0036_data_viewing_user_fix
# portal.migrations.0037_userprofile_developer
# portal.migrations.0041_new_news
# portal.migrations.0040_initial_news


def insert_admin_user(apps, schema_editor):
    User = apps.get_model("auth", "User")
    admin = User.objects.create()
    admin.username = "portaladmin"
    admin.email = ("codeforlife-portal@ocado.com",)
    admin.is_superuser = True
    admin.is_staff = True
    admin.password = make_password(os.getenv("ADMIN_PASSWORD", "abc123"))
    admin.save()


def insert_users(apps, schema_editor):
    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("portal", "UserProfile")
    School = apps.get_model("portal", "School")
    Teacher = apps.get_model("portal", "Teacher")
    Class = apps.get_model("portal", "Class")
    Student = apps.get_model("portal", "Student")

    # Create school
    school = School.objects.create(
        name="Swiss Federal Polytechnic",
        postcode="AL10 9NE",
        town="Welwyn Hatfield",
        latitude="51.76183",
        longitude="-0.244361",
    )

    # Create teachers' users
    teacher_user = User.objects.create(
        username="test teacher",
        first_name="Albert",
        last_name="Einstein",
        email="alberteinstein@codeforlife.com",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    teacher2_user = User.objects.create(
        username="test teacher2",
        first_name="Max",
        last_name="Planck",
        email="maxplanck@codeforlife.com",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    teacher3_user = User.objects.create(
        username="media ram",
        first_name="Ram",
        last_name="Leith",
        email="ramleith@codeforlife.com",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    # Create students' users
    student1_user = User.objects.create(
        username="test student1",
        first_name="Leonardo",
        last_name="DaVinci",
        email="leonardodavinci@codeforlife.com",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    student2_user = User.objects.create(
        username="test student2",
        first_name="Galileo",
        last_name="Galilei",
        email="galileogalilei@codeforlife.com",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    student3_user = User.objects.create(
        username="Issac",
        first_name="Isaac",
        last_name="Newton",
        email="isaacnewton@codeforlife.com",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    student4_user = User.objects.create(
        username="test student4",
        first_name="Richard",
        last_name="Feynman",
        email="richardfeynman@codeforlife.com",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    student5_user = User.objects.create(
        username="test student5",
        first_name="Alexander",
        last_name="Flemming",
        email="alexanderflemming@codeforlife.com",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    student6_user = User.objects.create(
        username="test student6",
        first_name="Daniel",
        last_name="Bernoulli",
        email="danielbernoulli@codeforlife.com",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    indy_user = User.objects.create(
        username="indy",
        first_name="Indiana",
        last_name="Jones",
        email="indianajones@codeforlife.com",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    student7_user = User.objects.create(
        username="media noah",
        first_name="Noah",
        last_name="Monaghan",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    student8_user = User.objects.create(
        username="media elliot",
        first_name="Elliot",
        last_name="Sharp",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    student9_user = User.objects.create(
        username="media tajmae",
        first_name="Tajmae",
        last_name="Joseph",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    student10_user = User.objects.create(
        username="media carlton",
        first_name="Carlton",
        last_name="Joseph",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    student11_user = User.objects.create(
        username="media nadal",
        first_name="Nadal",
        last_name="Spencer-Jennings",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    student12_user = User.objects.create(
        username="media freddie",
        first_name="Freddie",
        last_name="Goff",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    student13_user = User.objects.create(
        username="media leon",
        first_name="Leon",
        last_name="Scott",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    student14_user = User.objects.create(
        username="media betty",
        first_name="Betty",
        last_name="Kessell",
        password=make_password(os.getenv("ADMIN_PASSWORD", "Password1")),
    )

    # Create UserProfiles
    teacher_userprofile = UserProfile.objects.create(user=teacher_user, developer=True)
    teacher2_userprofile = UserProfile.objects.create(user=teacher2_user)
    teacher3_userprofile = UserProfile.objects.create(user=teacher3_user)
    student1_userprofile = UserProfile.objects.create(
        user=student1_user, developer=True
    )
    student2_userprofile = UserProfile.objects.create(user=student2_user)
    student3_userprofile = UserProfile.objects.create(user=student3_user)
    student4_userprofile = UserProfile.objects.create(user=student4_user)
    student5_userprofile = UserProfile.objects.create(user=student5_user)
    student6_userprofile = UserProfile.objects.create(user=student6_user)
    indy_userprofile = UserProfile.objects.create(user=indy_user)
    student7_userprofile = UserProfile.objects.create(user=student7_user)
    student8_userprofile = UserProfile.objects.create(user=student8_user)
    student9_userprofile = UserProfile.objects.create(user=student9_user)
    student10_userprofile = UserProfile.objects.create(user=student10_user)
    student11_userprofile = UserProfile.objects.create(user=student11_user)
    student12_userprofile = UserProfile.objects.create(user=student12_user)
    student13_userprofile = UserProfile.objects.create(user=student13_user)
    student14_userprofile = UserProfile.objects.create(user=student14_user)

    # Create teachers
    teacher = Teacher.objects.create(
        title="Mr",
        user=teacher_userprofile,
        school=school,
        is_admin=True,
        pending_join_request=None,
    )
    teacher2 = Teacher.objects.create(
        title="Mr",
        user=teacher2_userprofile,
        school=school,
        is_admin=False,
        pending_join_request=None,
    )
    teacher3 = Teacher.objects.create(
        title="Mrs",
        user=teacher3_userprofile,
        school=school,
        is_admin=True,
        pending_join_request=None,
    )

    # Create classes
    klass = Class.objects.create(
        name="Class 101",
        teacher=teacher,
        access_code="AB123",
        classmates_data_viewable=True,
        always_accept_requests=True,
    )
    class2 = Class.objects.create(
        name="Class 102",
        teacher=teacher2,
        access_code="AB124",
        classmates_data_viewable=True,
        always_accept_requests=True,
    )

    class3 = Class.objects.create(
        name="Class 103",
        teacher=teacher2,
        access_code="AB125",
        classmates_data_viewable=True,
        always_accept_requests=True,
    )

    class4 = Class.objects.create(
        name="Young Coders 101",
        teacher=teacher3,
        access_code="RL123",
        classmates_data_viewable=True,
        always_accept_requests=True,
    )

    # Create students
    student1 = Student.objects.create(
        class_field=klass, user=student1_userprofile, pending_class_request=None
    )

    student2 = Student.objects.create(
        class_field=klass, user=student2_userprofile, pending_class_request=None
    )

    student3 = Student.objects.create(
        class_field=None, user=student3_userprofile, pending_class_request=None
    )

    student4 = Student.objects.create(
        class_field=class2, user=student4_userprofile, pending_class_request=None
    )

    student5 = Student.objects.create(
        class_field=class2, user=student5_userprofile, pending_class_request=None
    )

    student6 = Student.objects.create(
        class_field=class3, user=student6_userprofile, pending_class_request=None
    )

    indy_student = Student.objects.create(
        user=indy_userprofile, pending_class_request=None
    )

    student7 = Student.objects.create(
        class_field=class4, user=student7_userprofile, pending_class_request=None
    )

    student8 = Student.objects.create(
        class_field=class4, user=student8_userprofile, pending_class_request=None
    )

    student9 = Student.objects.create(
        class_field=class4, user=student9_userprofile, pending_class_request=None
    )

    student10 = Student.objects.create(
        class_field=class4, user=student10_userprofile, pending_class_request=None
    )

    student11 = Student.objects.create(
        class_field=class4, user=student11_userprofile, pending_class_request=None
    )

    student12 = Student.objects.create(
        class_field=class4, user=student12_userprofile, pending_class_request=None
    )

    student13 = Student.objects.create(
        class_field=class4, user=student13_userprofile, pending_class_request=None
    )

    student14 = Student.objects.create(
        class_field=class4, user=student14_userprofile, pending_class_request=None
    )

    user = User.objects.create(
        username="DATA_AGGREGATE",
        first_name="DATA",
        last_name="AGGREGATE",
        email="aggregator@codeforlife.com",
        password=make_password(os.getenv("DATA_AGGREGATE_PASSWORD", "Password1")),
    )

    user_profile = UserProfile.objects.create(user=user, can_view_aggregated_data=True)


def insert_news(apps, schema_editor):
    FrontPageNews = apps.get_model("portal", "FrontPageNews")

    news1 = FrontPageNews.objects.create(
        title="Teachers 'not confident on coding'",
        text="Computer coding is being introduced to the school curriculum in less than six weeks' time, but many primary school teachers will be under-prepared to teach the new subject, according to a new poll.",
        link="http://www.dailymail.co.uk/wires/pa/article-2700124/TEACHERS-NOT-CONFIDENT-ON-CODING.html?ITO=1490&ns_mchannel=rss&ns_campaign=1490",
        link_text="Read more on www.dailymail.co.uk",
        added_dstamp=timezone.now(),
    )
    news2 = FrontPageNews.objects.create(
        title="British schools are not prepared to teach coding",
        text="With just six weeks until the new computing curriculum is introduced in UK schools, research has revealed that British primary school teachers are not fully prepared to teach their pupils how to code.",
        link="http://www.cbronline.com/news/social/british-teachers-are-not-prepared-to-teach-coding-4322259",
        link_text="Read more on www.cbronline.co.uk",
        added_dstamp=timezone.now(),
    )
    news3 = FrontPageNews.objects.create(
        title="Ocado launches free Code For Life tool to help 130,000 apprehensive primary school teachers",
        text="Thousands of primary school teachers aren’t ready to teach computer coding lessons that become part of the country’s national curriculum for computing before the start of the academic year in September.",
        link="http://www.itproportal.com/2014/07/21/ocado-launches-free-code-life-tool-help-130000-apprehensive-primary-school-teachers/?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+itproportal%2Frss+(Latest+ITProPortal+News)",
        link_text="Read more on itproportal.com",
        added_dstamp=timezone.now(),
    )
    news4 = FrontPageNews.objects.create(
        title="Ocado Technology launches coding resources for teachers",
        text="Ocado Technology is the latest business to get involved with preparing teachers for the new computing curriculum that comes into effect in September",
        link="http://www.computerworlduk.com/news/careers/3531070/ocado-technology-launches-coding-resources-for-teachers/",
        link_text="Read more on www.computerworlduk.com",
        added_dstamp=timezone.now(),
    )
    news5 = FrontPageNews.objects.create(
        title="Not Enough Teachers Will Know Code By September",
        text="A new curriculum brings coding into primary schools in September – and it looks as if teachers won’t be able to cope. ",
        link="http://www.techweekeurope.co.uk/news/not-enough-teachers-know-code-149462",
        link_text="Read more on www.techweekeurope.co.uk",
        added_dstamp=timezone.now(),
    )
    news6 = FrontPageNews.objects.create(
        title="Ocado Technology readies primary school teachers with code initiative",
        text="Ocado Technology has launched a coding initiative after finding that 73% of primary school teachers feel they have not been given the necessary resources to teach children to code.",
        link="http://www.computerweekly.com/news/2240225117/Ocado-Technology-readies-primary-school-teachers-with-code-initiative",
        link_text="Read more on www.computerweekly.com",
        added_dstamp=timezone.now(),
    )
    news7 = FrontPageNews.objects.create(
        title="Curriculum countdown",
        text="According to new research more than 130,000 primary school teachers don’t feel confident enough to teach computer coding",
        link="http://edtechnology.co.uk/Featured-Content/curriculum_countdown",
        link_text="Read more on www.edtechnology.co.uk",
        added_dstamp=timezone.now(),
    )
    news8 = FrontPageNews.objects.create(
        title="Computing Curriculum Countdown: Over 130,000 Primary School Teachers Don’t Feel Confident Enough to Teach Computer Coding",
        text="Many primary school teachers feel they haven’t been given the necessary resources to teach the new Computing curriculum from September. ",
        link="http://www.primarytimes.net/news/2014/07/computing-curriculum-countdown-over-130-000-primary-school-teachers-don-t-feel-confident-enough-to-teach-computer-coding-",
        link_text="Read more on www.primarytimes.net",
        added_dstamp=timezone.now(),
    )
    news9 = FrontPageNews.objects.create(
        title="Ocado’s technology team to release primary school coding tool",
        text="Ocado’s technology team is launching Code for Life, the online grocer’s initiative to help children learn to code.",
        link="http://internetretailing.net/2014/07/ocados-technology-team-launch-primary-school-coding-tool/",
        link_text="Read more on www.internetretailing.net",
        added_dstamp=timezone.now(),
    )
    news10 = FrontPageNews.objects.create(
        title="Teachers 'not confident' over coding",
        text="Computer coding is being introduced to the school curriculum in less than six weeks' time, but many primary school teachers will be under-prepared to teach the new subject, according to a new poll.",
        link="http://www.dailyecho.co.uk/leisure/technology/11358091.Teachers__not_confident__over_coding/",
        link_text="Read more on www.dailyecho.co.uk",
        added_dstamp=timezone.now(),
    )
    news11 = FrontPageNews.objects.create(
        title="Ocado Technology launches coding resources for teachers",
        text="Ocado Technology is a latest business to get concerned with scheming teachers for a new computing curriculum that comes into outcome in September.",
        link="http://www.datacentremanagement.org/2014/07/ocado-technology-launches-coding-resources-for-teachers/",
        link_text="Read more on www.datacentremanagement.org",
        added_dstamp=timezone.now(),
    )
    news12 = FrontPageNews.objects.create(
        title="Teachers 'not confident enough' to teach code",
        text="More than 70% of primary school teachers say they don't feel confident enough to teach the new coding syllabus being introduced this September.",
        link="http://www.newelectronics.co.uk/electronics-news/teachers-not-confident-enough-to-teach-code/62697/",
        link_text="Read more on www.newelectronics.co.uk",
        added_dstamp=timezone.now(),
    )


def insert_news2(apps, schema_editor):
    FrontPageNews = apps.get_model("portal", "FrontPageNews")

    news1 = FrontPageNews.objects.create(
        title="Bletchley Park: From Code-Breaking to Kids Coding",
        text="The National Museum of Computer has opened its free Weekend Codability Project. This is part of the Code for Life initiative which aims to inspire the next generation of computer scientists.",
        link="http://www.idgconnect.com/blog-abstract/9056/bletchley-park-from-code-breaking-kids-coding",
        link_text="Read more on idgconnect.com",
        added_dstamp=timezone.now(),
    )
    news2 = FrontPageNews.objects.create(
        title="Giving kids Codability",
        text="Weekend Codability aims to empower young people by introducing them to programming computers. Children will be taught how to give instructions to computers, change existing instructions in programs and create their own programs.",
        link="http://edtechnology.co.uk/News/giving_kids_codability",
        link_text="Read more on edtechnology.co.uk",
        added_dstamp=timezone.now(),
    )
    news3 = FrontPageNews.objects.create(
        title="Try your hand at Bletchley Park codability project",
        text="Following the introduction of computing to England’s school curriculum last month, young people across the country are being invited to try their hand at programming computers in Block H, the world's first purpose-built computer centre, on Bletchley Park.",
        link="http://www.mkweb.co.uk/COMPUTERS-Try-hand-Bletchley-Park-codability/story-23860128-detail/story.html",
        link_text="Read more on mkweb.co.uk",
        added_dstamp=timezone.now(),
    )


class Migration(migrations.Migration):

    replaces = [
        ("portal", "0001_initial"),
        ("portal", "0002_admin_user"),
        ("portal", "0003_school_teacher_relationship"),
        ("portal", "0004_class_access_code"),
        ("portal", "0005_student_pin"),
        ("portal", "0006_teacher_email_verification"),
        ("portal", "0007_school_admin"),
        ("portal", "0008_auto_20140729_0938"),
        ("portal", "0009_remove_student_pin"),
        ("portal", "0010_auto_20140729_1030"),
        ("portal", "0009_teacher_pending_join_request"),
        ("portal", "0011_merge"),
        ("portal", "0012_auto_20140729_1359"),
        ("portal", "0013_auto_20140730_1100"),
        ("portal", "0014_auto_20140730_1459"),
        ("portal", "0015_student_pending_class_request"),
        ("portal", "0016_emailverification_email"),
        ("portal", "0017_school_postcode"),
        ("portal", "0018_auto_20140804_1246"),
        ("portal", "0019_auto_20140804_1713"),
        ("portal", "0020_auto_20140806_1632"),
        ("portal", "0020_auto_20140806_1205"),
        ("portal", "0021_merge"),
        ("portal", "0022_remove_student_name"),
        ("portal", "0023_class_classmates_data_viewable"),
        ("portal", "0024_auto_20140813_1536"),
        ("portal", "0025_trial_users"),
        ("portal", "0026_fix_trial_users"),
        ("portal", "0027_more_trial_users"),
        ("portal", "0028_demoting_max_planck"),
        ("portal", "0029_trial_independent_student"),
        ("portal", "0030_media_users"),
        ("portal", "0031_auto_20140903_1450"),
        ("portal", "0032_userprofile_can_view_aggregated_data"),
        ("portal", "0033_data_viewing_user"),
        ("portal", "0034_data_viewing_user_fix"),
        ("portal", "0035_data_viewing_user_hack"),
        ("portal", "0036_data_viewing_user_fix"),
        ("portal", "0037_userprofile_developer"),
        ("portal", "0038_frontpagenews"),
        ("portal", "0039_auto_20141109_1827"),
        ("portal", "0040_initial_news"),
        ("portal", "0041_new_news"),
    ]

    dependencies = [
        ("auth", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "avatar",
                    models.ImageField(
                        default="static/portal/img/avatars/default-avatar.jpeg",
                        null=True,
                        upload_to="static/portal/img/avatars/",
                        blank=True,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
                ("awaiting_email_verification", models.BooleanField(default=False)),
                ("can_view_aggregated_data", models.BooleanField(default=False)),
                ("developer", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="School",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("postcode", models.CharField(max_length=10)),
                ("latitude", models.CharField(max_length=20)),
                ("longitude", models.CharField(max_length=20)),
                ("town", models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name="Teacher",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        to="portal.UserProfile", on_delete=models.CASCADE
                    ),
                ),
                (
                    "pending_join_request",
                    models.ForeignKey(
                        related_name="join_request",
                        to="portal.School",
                        null=True,
                        on_delete=models.SET_NULL,
                    ),
                ),
                ("is_admin", models.BooleanField(default=False)),
                ("title", models.CharField(max_length=35)),
                (
                    "school",
                    models.ForeignKey(
                        related_name="teacher_school",
                        to="portal.School",
                        null=True,
                        on_delete=models.SET_NULL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Class",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("access_code", models.CharField(max_length=5)),
                ("classmates_data_viewable", models.BooleanField(default=False)),
                ("accept_requests_until", models.DateTimeField(null=True)),
                ("always_accept_requests", models.BooleanField(default=False)),
                (
                    "teacher",
                    models.ForeignKey(
                        related_name="class_teacher",
                        to="portal.Teacher",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"verbose_name_plural": "classes"},
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "class_field",
                    models.ForeignKey(
                        related_name="students",
                        to="portal.Class",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        to="portal.UserProfile", on_delete=models.CASCADE
                    ),
                ),
                (
                    "pending_class_request",
                    models.ForeignKey(
                        related_name="class_request",
                        to="portal.Class",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Guardian",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("children", models.ManyToManyField(to="portal.Student")),
                (
                    "user",
                    models.OneToOneField(
                        to="portal.UserProfile", on_delete=models.CASCADE
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EmailVerification",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("token", models.CharField(max_length=30)),
                ("expiry", models.DateTimeField()),
                ("used", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        related_name="email_verifications",
                        to="portal.UserProfile",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "email",
                    models.CharField(
                        default=None, max_length=200, null=True, blank=True
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FrontPageNews",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("text", models.CharField(max_length=1000)),
                ("link", models.CharField(max_length=500)),
                ("link_text", models.CharField(max_length=200)),
                ("added_dstamp", models.DateTimeField()),
            ],
        ),
        migrations.RunPython(code=insert_admin_user),
        migrations.RunPython(code=insert_users),
        migrations.RunPython(code=insert_news),
        migrations.RunPython(code=insert_news2),
    ]
