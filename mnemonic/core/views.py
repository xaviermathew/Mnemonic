from django.shortcuts import render


def qs_to_options(qs, label_field, value_field):
    options = []
    for obj in qs:
        options.append({
            'label': getattr(obj, label_field),
            'value': getattr(obj, value_field),
        })
    return options


def home(request):
    from mnemonic.entity.models import Person
    from mnemonic.news.models import NewsSource
    from mnemonic.news.utils.search_utils import get_search_results, get_client

    twitter_users = qs_to_options(Person.objects.all(), 'name', 'name')
    ctx = {
        'num_docs': get_client().count(),
        'newspapers_options': qs_to_options(NewsSource.objects.all(), 'name', 'name'),
        'twitter_handles_options': twitter_users,
        'twitter_mentions_options': twitter_users,
        'has_query': any(v for v in request.GET.values())
    }
    q = request.GET.get('query')
    if q:
        ctx.update(request.GET)
        ctx['num_results'], ctx['results'] = get_search_results(**request.GET)
    return render(request, 'home.html', ctx)


def about(request):
    ctx = {
    }
    return render(request, 'about.html', ctx)


def stories(request):
    from mnemonic.stories.models import Dashboard

    ctx = {
        'stories': Dashboard.objects.filter(name__startswith='Story:', is_archived=False, is_draft=False)
    }
    return render(request, 'stories.html', ctx)


def story(request, slug):
    from mnemonic.stories.models import Dashboard

    ctx = {
        'story': Dashboard.objects.get(name__startswith='Story:', is_archived=False, is_draft=False, slug=slug)
    }
    return render(request, 'story.html', ctx)
