from django.contrib import admin

from movie_recommendation_api.movie import models


class RoleInline(admin.TabularInline):
    """
    Inline admin class for the Role model.

    This class allows adding and editing Role objects directly from the
    Movie and CastCrew admin pages. It uses an autocomplete field for the
    cast_crew field to make it easier to select a related CastCrew object.
    """

    model = models.Role
    extra = 1
    autocomplete_fields = ['cast_crew']


class RatingsInline(admin.TabularInline):
    """
    Inline admin class for the Rating model.

    This class allows adding and editing Rating objects directly from the
    Movie admin page. It uses an autocomplete field for the user field to
    make it easier to select a related user.
    """

    model = models.Rating
    extra = 1
    autocomplete_fields = ['user']


@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Movie model.

    This class customizes the list view by displaying the title, release date,
    and runtime of each movie. It also adds search fields for the title and
    release date, and an autocomplete field for the genre. It pre-populates
    the slug field based on the title, and includes the RatingsInline and
    RoleInline inlines to allow adding and editing related ratings and roles
    directly from the movie admin page.
    """

    list_display = [
        'title',
        'release_date',
        'runtime'
    ]
    search_fields = ['title__istartswith', 'release_date']
    autocomplete_fields = ['genre']

    prepopulated_fields = {
        'slug': ['title']
    }

    # Inlines to display related models directly on the movie admin page
    inlines = [RatingsInline, RoleInline]


@admin.register(models.Rating)
class RatingAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Rating model.

    This class adds a search field for the movie and displays the user
    and the movie in the list view.
    """

    search_fields = ['movie']
    list_display = [
        'user',
        'movie'
    ]


@admin.register(models.CastCrew)
class CastCrewAdmin(admin.ModelAdmin):
    """
    Custom admin class for the CastCrew model.

    This class adds a search field for the name, displays the name and career
    in the list view, and includes the RoleInline inline to allow adding and
    editing related roles directly from the cast/crew admin page.
    """

    search_fields = ['name']
    # autocomplete_fields = ['role']
    list_display = [
        'name',
    ]
    inlines = [RoleInline]


@admin.register(models.Career)
class CareersAdmin(admin.ModelAdmin):
    """

    """

    search_fields = ['name']
    list_display = [
        'name'
    ]


@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Role model.

    This class adds a search field for the name and displays the name in
    the list view.
    """

    search_fields = ['name']
    list_display = [
        'name'
    ]


@admin.register(models.Genre)
class GenreAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Genre model.

    This class adds a search field for the title and prepopulates the slug
    field based on the title.
    """

    search_fields = ['title']
    prepopulated_fields = {
        'slug': ['title']
    }


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Review model.

    This custom admin class is used to configure the administration interface
    for the Review model. It defines how reviews are displayed and searched
    within the admin panel.

    Attributes:
        search_fields (list): A list of fields that can be searched for reviews
            within the admin panel. In this case, 'user' is searchable.
        list_display (list): A list of fields that will be displayed in the list
            view of reviews within the admin panel. In this case, only 'user'
            is displayed.
    """

    search_fields = ['user']
    list_display = [
        'user'
    ]
