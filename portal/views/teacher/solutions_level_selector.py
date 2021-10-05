from __future__ import division
from builtins import str
import game.messages as messages
from django.template import RequestContext
from django.utils.safestring import mark_safe

from game.models import Episode
from django.core.cache import cache
from game import app_settings
from common.permissions import logged_in_as_teacher
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404


def fetch_episode_data_from_database(early_access):
    episode_data = []
    episode = Episode.objects.get(pk=1)
    while episode is not None:
        if episode.in_development and not early_access:
            break

        levels, minName, maxName = min_max_levels(episode.levels)

        e = {
            "id": episode.id,
            "name": episode.name,
            "levels": levels,
            "first_level": minName,
            "last_level": maxName,
            "random_levels_enabled": episode.r_random_levels_enabled,
        }

        episode_data.append(e)
        episode = episode.next_episode
    return episode_data


def min_max_levels(episode_levels):
    levels = []
    minName = 1000
    maxName = 0

    for level in episode_levels:
        level_name = int(level.name)
        if level_name > maxName:
            maxName = level_name
        if level_name < minName:
            minName = level_name

        levels.append(
            {"id": level.id, "name": level_name, "title": get_level_title(level_name)}
        )

    return levels, minName, maxName


def fetch_episode_data(early_access):
    key = "episode_data"
    if early_access:
        key = "episode_data_early_access"
    data = cache.get(key)
    if data is None:
        data = fetch_episode_data_from_database(early_access)
        cache.set(key, data)
    return data


def get_level_title(i):
    title = "title_level" + str(i)
    try:
        titleCall = getattr(messages, title)
        return mark_safe(titleCall())
    except AttributeError:
        return ""


@login_required(login_url=reverse_lazy("teach"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teach"))
def levels(request):
    """Loads a page with all levels listed.

    **Context**

    ``RequestContext``
    ``episodes``

    **Template:**

    :template:`game/level_selection.html`
    """

    episode_data = fetch_episode_data(app_settings.EARLY_ACCESS_FUNCTION(request))

    return render(
        request,
        "portal/teach/teacher_level_solutions.html",
        {"episodeData": episode_data},
    )
