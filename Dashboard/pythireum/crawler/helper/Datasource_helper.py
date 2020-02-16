from ..models import Datasource
from django.http import Http404

class Datasource_helper():
    datasource_web_exist = False
    datasource_socialnetwork_exist = False
    datasource_custom_exist = False
    # Return 3 boolean in that order: web_exist, custom_exist, socialnetwork_exist
    def get_datasource_types(self):
        try:
            datasources = Datasource.objects.all()
        except Datasource.DoesNotExist:
            raise Http404("There is no datasources")
        for d in datasources:
            if d.type == "web":
                self.datasource_web_exist = True
            elif d.type == "socialnetwork":
                self.datasource_socialnetwork_exist = True
            elif d.type == "custom":
                self.datasource_custom_exist = True
        return self.datasource_web_exist, self.datasource_socialnetwork_exist, self.datasource_custom_exist
