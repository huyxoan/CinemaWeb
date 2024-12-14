from django.db.models import Count
from django.views.generic import DetailView, ListView

from .models import Serie, Film, Part, Season, FilmByQuality, FilmVisit, SerieVisit, Genre, Date
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.http import HttpResponse



from django.utils.translation import activate





class SerieComponent(DetailView):
    template_name = 'serie_download_page.html'
    model = Serie
    context_object_name = 'serie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loaded_serie = self.object
        context['seasons'] = Season.objects.filter(serie__slug=loaded_serie.slug).all()
        context['parts'] = Part.objects.filter(season__serie__slug=loaded_serie.slug).all()
        context['trailer'] = loaded_serie.trailer.url if loaded_serie.trailer else None
        context['related_series'] = Serie.objects.filter(genre=loaded_serie.genre.first()).exclude(pk=loaded_serie.id)
        if self.request.user.is_authenticated:
            context['is_favorite'] = self.request.user.saved_series.filter(pk=loaded_serie.id).exists()




        return context

from django.utils import timezone
from transformers import pipeline


sentiment_analyzer = pipeline("sentiment-analysis")
class FilmComponent(DetailView):
    template_name = 'film_download_page.html'
    model = Film
    context_object_name = 'film'

    def get(self, request, *args, **kwargs):
        # Language activation logic
        lang_code = request.GET.get('lang', 'vn')
        activate(lang_code)
        request.session['django_language'] = lang_code

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loaded_film = self.object
        context['film_qualities'] = FilmByQuality.objects.prefetch_related().filter(film__slug=loaded_film.slug).all()
        context['related_films'] = Film.objects.filter(genre=loaded_film.genre.first()).exclude(pk=loaded_film.id)
        context['trailer'] = loaded_film.trailer.url if loaded_film.trailer else None

       
        

        if self.request.user.is_authenticated:
            context['is_favorite'] = self.request.user.saved_films.filter(pk=loaded_film.id).exists()


        return context
    



class FilmList(ListView):
    template_name = 'films_page.html'
    model = Film
    context_object_name = 'films'
    ordering = ['-imdb']
    paginate_by = 6

    def get(self, request, *args, **kwargs):
        # Language activation logic
        lang_code = request.GET.get('lang', 'vn')
        activate(lang_code)
        request.session['django_language'] = lang_code

        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['most_visit'] = Film.objects.filter(is_active=True).annotate(
            visit_count=Count('filmvisit')).order_by('-visit_count')[:8]
        context['all_genres'] = Genre.objects.all()
        context['all_years'] = Date.objects.all()
        # film_ids = context['films'].values_list('id', flat=True)  # Get the list of film IDs
        # context['shows'] = Shows.objects.filter(film_id__in=film_ids)

        return context


class SerieList(ListView):
    template_name = 'series_page.html'
    model = Serie
    context_object_name = 'series'
    ordering = ['-imdb']
    paginate_by = 6

    def get(self, request, *args, **kwargs):
        # Language activation logic
        lang_code = request.GET.get('lang', 'vn')
        activate(lang_code)
        request.session['django_language'] = lang_code

        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['most_visit'] = Serie.objects.filter(is_active=True).annotate(
            visit_count=Count('serievisit')).order_by('-visit_count')[:8]
        context['all_genres'] = Genre.objects.all()
        context['all_years'] = Date.objects.all()

        return context
        