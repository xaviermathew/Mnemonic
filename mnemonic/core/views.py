import urllib.parse

from django.shortcuts import render, get_object_or_404


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

    twitter_users = qs_to_options(Person.objects.all(), 'name', 'twitter_handle')
    query_keys = {'query', 'source_types', 'newspapers', 'twitter_handles',
                  'twitter_mentions', 'start_date', 'end_date'}
    query_params = {k: v for k, v in dict(request.GET).items()
                    if k in query_keys and ((isinstance(v, list) and v[0]) or v)}
    ctx = {
        'num_docs': get_client().count(),
        'newspapers_options': qs_to_options(NewsSource.objects.all(), 'name', 'name'),
        'twitter_handles_options': twitter_users,
        'twitter_mentions_options': twitter_users,
        'has_query': bool(query_params)
    }
    if query_params:
        ctx.update(query_params)
        ctx['num_results'], ctx['results'] = get_search_results(**query_params)
        ctx['twitter_lookup'] = {d['value']: d['label'] for d in twitter_users}
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

    qs = Dashboard.objects.filter(name__startswith='Story:', is_archived=False, is_draft=False, slug=slug)
    ctx = {
        'story': get_object_or_404(qs)
    }
    return render(request, 'dashboard.html', ctx)


def people(request):
    from mnemonic.entity.models import Person

    ctx = {
        'people': Person.objects.order_by('name')
    }
    return render(request, 'people.html', ctx)


def person(request, pk):
    from mnemonic.entity.models import Person
    from mnemonic.stories.models import Dashboard

    dashboard_qs = Dashboard.all_objects.filter(name='Person profile', is_archived=False, is_draft=False)
    person_qs = Person.objects.filter(pk=pk)
    person = get_object_or_404(person_qs)
    ctx = {
        'person': person,
        'story': get_object_or_404(dashboard_qs),
        'params': urllib.parse.urlencode({'p_twitter_handle': person.name})
    }
    return render(request, 'dashboard.html', ctx)
