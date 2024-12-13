from itertools import chain

from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View

from home_app.models import Slider, HomePageSlider, SiteSetting
from movie_app.models import Film, Serie, Genre, Date
from django.utils.translation import activate

class HomeView(View):
    @staticmethod
    def get(request):
        # Handle language activation
        lang_code = request.GET.get('lang', 'vn')
        if lang_code in ['vn', 'en']:
           activate(lang_code)
           request.session['django_language'] = lang_code

        # Get the first active HomePageSlider instance (or None if none are active)
        homepage_slider = HomePageSlider.objects.filter(is_active=True).first()

        context = {
            'slider': Slider.objects.filter(is_active=True).first(),
            'latest_added_films': Film.objects.filter(is_active=True).order_by('-id')[:5],  # Last 5 films
            'latest_added_series': Serie.objects.filter(is_active=True).order_by('-id')[:5],  # Last 5 series
            'recent_series': homepage_slider.recent_series_slider_2.all() if homepage_slider else [],
            'recent_films': homepage_slider.recent_films_slider_1.all() if homepage_slider else [],
            'all_genres': Genre.objects.all(),
        }

        return render(request, 'index.html', context)


class GenreFilterList(View):
    @staticmethod
    def get(request, genre):
        films = Film.objects.filter(genre__genre__contains=genre).all()
        series = Serie.objects.filter(genre__genre__contains=genre).all()
        movies = list(chain(films, series))
        paginator = Paginator(movies, 4)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)
        context = {
            'page': page_obj,
            'paginator': paginator,
        }
        return render(request, 'genre_filter_page.html', context)


class YearFilterList(View):
    @staticmethod
    def get(request, year):
        films = Film.objects.filter(release_date__date__year=year).all()
        series = Serie.objects.filter(release_date__date__year=year).all()
        movies = list(chain(films, series))
        paginator = Paginator(movies, 4)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)
        context = {
            'page': page_obj,
            'paginator': paginator,
        }
        return render(request, 'genre_filter_page.html', context)


# /search/?movie=
def search_box(request):
    movie = request.GET.get('movie')
    movies = []
    if movie:
        films = Film.objects.filter(name__icontains=movie)
        series = Serie.objects.filter(name__icontains=movie)

        for film in films:
            movies.append({'label': film.name, 'url': film.get_absolute_url(), 'img': film.banner.url})
        for serie in series:
            movies.append({'label': serie.name, 'url': serie.get_absolute_url(), 'img': serie.banner.url})

    return JsonResponse(movies, safe=False)


def header(request: HttpResponse):
    return render(request, '_shared/header.html', {})


def footer(request: HttpResponse):
    return render(request, '_shared/footer.html', {'settings': SiteSetting.objects.filter(is_active=True).first()})


def genres(request):
    return render(request, 'genres_component.html', {'all_genres': Genre.objects.all()})


def years(request):
    return render(request, 'years_component.html', {'all_years': Date.objects.all()})


def cartoons(request):
    return render(request, 'cartoons_component.html', {
        'cartoons': list(chain(Film.objects.filter(genre__genre__contains="animation"),
                               Serie.objects.filter(genre__genre__contains="animation")))
    }
                  )


def handler_404(request, exception):
    return render(request, '_shared/404.html', status=404)
