from django.db import models

# Create your models here.


class Datasource(models.Model):
    name = models.CharField(max_length=50, default="Data source name")
    short_description = models.CharField(max_length=200, default="Short and concise description")
    description = models.CharField(max_length=1000, default="Detailed description")
    url = models.CharField(max_length=200, default="http://")
    # web or socialnetwork or custom
    type = models.CharField(max_length=40, default="web")
    parsing_in_progress = models.BooleanField(default=False)

    def __str__(self):
        return self.name + "-type-" +self.type


class Value(models.Model):
    parent_search = models.CharField(max_length=50, blank=False)
    origin_source = models.CharField(max_length=50, blank=False)
    key = models.CharField(max_length=200, blank=False)
    value = models.CharField(max_length=400, blank=False)
    date =  models.DateField(blank=False)

class Search(models.Model):
    name = models.CharField(max_length=50, default="Data source name")
    chosen_datasource = models.ManyToManyField(Datasource, blank=True)
    # coma separated list of keyword to use for the search
    keywords = models.CharField(max_length=200, default="Blockchain")
    date =  models.DateField(auto_now_add=True)
    # running or stopped for now
    status = models.CharField(max_length=40, default="running")
    deleted = models.BooleanField(default=False)

    # coma separated list of search's threadID
    crawler_thread_ids = models.CharField(max_length=200, default="-1")
    crawled_values = models.ManyToManyField(Value, blank=True)
    parsing_in_progress = models.BooleanField(default=False)







