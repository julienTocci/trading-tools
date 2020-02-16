from django.shortcuts import render, get_object_or_404
from django.http import Http404

from .models import Datasource
from .models import Search
from .models import Value

from .helper import nlp_helper
from .helper import Datasource_helper

import datetime
import importlib
import time
import boto3

datasource_helper = Datasource_helper.Datasource_helper()
nlp_helper_instance = nlp_helper.NLP_helper()

client = boto3.client('s3', region_name='us-east-1')

datasource_web_exist, datasource_socialnetwork_exist, datasource_custom_exist = datasource_helper.get_datasource_types()

all_datasource = Datasource.objects.all()
all_search = Search.objects.all()
crawler_threads = []
unique_crawler_thread_id = 0
parser_threads = []


verified_values = {}

unique_parser_thread_id = 0


def main(request):
    global all_search

    last_hundred_values = Value.objects.all().order_by('-id')[:100]

    count = 0
    for search_dict in verified_values:
        count += len(verified_values[search_dict])

    return render(request, 'crawler/main.html', {     "verified_values_count": count,
                                                      "verified_values": verified_values,
                                                      "number_crawler_value": nlp_helper_instance.total_found_value,
                                                      "request_analyzed": nlp_helper_instance.total_request_analyzed,
                                                      "last_hundred_in_ascending_order": last_hundred_values,
                                                      "all_search": all_search,
                                                      "datasource_web_exist": datasource_web_exist,
                                                      "datasource_custom_exist": datasource_custom_exist,
                                                      "datasource_socialnetwork_exist": datasource_socialnetwork_exist})



def blockchain(request):

    if request.method == 'POST':
        search_name = request.POST['name']

        for v in Value.objects.filter(parent_search=search_name):
            verified = False
            for other_value in  Value.objects.filter(parent_search=search_name, key=v.key).exclude(origin_source=v.origin_source):
                # Other value with same key and different origin sources
                if other_value.value == v.value:
                    verified = True
                else:
                    verified =False
            if verified:
                if search_name not in verified_values:
                    verified_values[search_name] = []
                print("Appending verified value: ", v.key, v.value)
                verified_values[search_name].append({"key": v.key, "value":v.value})


    return render(request, 'crawler/blockchain_gate.html', {
                                                        "search_list": all_search,
                                                        "verified_values": verified_values,
                                                      "datasource_web_exist": datasource_web_exist,
                                                      "datasource_custom_exist": datasource_custom_exist,
                                                      "datasource_socialnetwork_exist": datasource_socialnetwork_exist})


def datasource_list(request, datasource_type):

    try:
        datasources = Datasource.objects.filter(type=datasource_type)
    except Datasource.DoesNotExist:
        raise Http404("There is no datasources")
    return render(request, 'crawler/datasourceList.html', {'datasources': datasources,
                                                           "datasource_web_exist": datasource_web_exist,
                                                           "datasource_custom_exist": datasource_custom_exist,
                                                           "datasource_socialnetwork_exist": datasource_socialnetwork_exist
                                                           })


def datasource(request, datasource_type, datasource_name):

    datasource = get_object_or_404(Datasource, name=datasource_name)

    return render(request, 'crawler/datasource.html', {'ds': datasource,
                                                       "datasource_web_exist": datasource_web_exist,
                                                       "datasource_custom_exist": datasource_custom_exist,
                                                       "datasource_socialnetwork_exist": datasource_socialnetwork_exist
                                                       })




def search(request):
    global all_search

    if request.method == 'POST':
        fail_key = False
        fail_ds = False
        fail_name = False
        existing_name = False

        keywords = request.POST['keywords']
        search_name = request.POST['name']
        try:
            if len(keywords) == 0:
                fail_key = True

            if len(search_name) == 0:
                fail_name = True

            for s in all_search:
                if s.deleted == False:
                    if s.name == search_name:
                        existing_name = True

            selected_datasource = []
            for ds in all_datasource:
                if request.POST[ds.name]:
                    selected_datasource.append(ds)
                    print(ds.name)

            if len(selected_datasource) == 0:
                fail_ds = True

            if fail_ds or fail_key or fail_name or existing_name:
                raise KeyError('Form incomplete')
        except(KeyError):
            return render(request, 'crawler/search.html', { "existing_name": existing_name,
                                                            "missing_ds": fail_ds,
                                                            "missing_name": fail_name,
                                                            "missing_keywords": fail_key,
                                                            "datasources": all_datasource,
                                                            "datasource_web_exist": datasource_web_exist,
                                                            "datasource_custom_exist": datasource_custom_exist,
                                                            "datasource_socialnetwork_exist": datasource_socialnetwork_exist})



        # Create Search object and start the crawlers

        # Populating thread id list for the Search object
        threadid_list = create_search_threadid_list(len(selected_datasource))

        new_search = Search.objects.create(crawler_thread_ids=threadid_list, name=search_name,keywords=keywords, date=datetime.datetime.now(), status="running")
        all_search = Search.objects.all()
        create_search_crawler(keywords, new_search, selected_datasource, False)

        print(crawler_threads)
        return render(request, 'crawler/search.html', {"valid_form": True,
                                                       "datasources": all_datasource,
                                                       "datasource_web_exist": datasource_web_exist,
                                                       "datasource_custom_exist": datasource_custom_exist,
                                                       "datasource_socialnetwork_exist": datasource_socialnetwork_exist})

    return render(request, 'crawler/search.html',  {
                                                    "datasources": all_datasource,
                                                    "datasource_web_exist": datasource_web_exist,
                                                      "datasource_custom_exist": datasource_custom_exist,
                                                      "datasource_socialnetwork_exist": datasource_socialnetwork_exist})




def searchpage(request, search_name):
    global unique_parser_thread_id

    search = get_object_or_404(Search, name=search_name)
    crawled_values = Value.objects.filter(parent_search=search.name)

    if request.is_ajax():
        if request.method == 'POST':
            search.parsing_in_progress = True
            search.save()
            print("Starting parsing of each datasource's data stored on S3")


            for d in search.chosen_datasource.all():
                    d.parsing_in_progress = True
                    module_name = ".datasources." + d.type + "." + d.name + "_parser"
                    class_name = d.name + "Parser"
                    module = importlib.import_module(module_name, package="crawler")
                    class_ = getattr(module, class_name)
                    keywords = search.keywords.split(",")
                    parser = class_(unique_parser_thread_id, keywords, search, nlp_helper_instance, client)
                    unique_parser_thread_id = unique_parser_thread_id + 1
                    parser_threads.append(parser)
                    parser.start()

    return render(request, 'crawler/search_page.html',  { "crawled_values": crawled_values,
                                                        "search": search,
                                                        "datasource_web_exist": datasource_web_exist,
                                                      "datasource_custom_exist": datasource_custom_exist,
                                                      "datasource_socialnetwork_exist": datasource_socialnetwork_exist})


def searchlist(request):
    global all_search
    global unique_crawler_thread_id

    if request.is_ajax():
        if request.method == 'POST':
            s = Search.objects.get(name=request.POST["name"])  # .delete()
            threadid_list = s.crawler_thread_ids.split(",")

            if(request.POST["action"] == "pause" or request.POST["action"] == "resume"):
                if s.status == "stopped":
                    s.status = "running"
                    # Restarting the threads, for now there is no stateful restart, it begins again from 0
                    # Populating thread id list for the Search object
                    threadid_list = create_search_threadid_list(s.chosen_datasource.count())
                    s.crawler_thread_ids = threadid_list
                    s.save()
                    create_search_crawler(s.keywords, s, s.chosen_datasource.all(), True)


                elif s.status == "running":
                    s.status = "stopped"
                    # The twitter crawler stop only when he receives a new twee and trigger the on_data()
                    # if it is the first to be stopped, it will delay the stopping
                    for id in threadid_list:
                        crawler_threads[int(id)].status = "stopped"
                        crawler_threads[int(id)].join()
                s.save()
            if(request.POST["action"] == "delete"):
                s = Search.objects.get(name=request.POST["name"]) #.delete()
                s.deleted = True
                s.status = "finished"
                for id in threadid_list:
                    crawler_threads[int(id)].status = "finished"
                    crawler_threads[int(id)].join()
                s.save()


    all_search = Search.objects.all()
    searchlist = Search.objects.filter(deleted=False)

    return render(request, 'crawler/search_list.html',  {
                                                        "search_list": searchlist,
                                                        "datasource_web_exist": datasource_web_exist,
                                                      "datasource_custom_exist": datasource_custom_exist,
                                                      "datasource_socialnetwork_exist": datasource_socialnetwork_exist})



def create_search_crawler(keywords, new_search, selected_datasource, already_created_search):
    global unique_crawler_thread_id
    for ds in selected_datasource:
        if already_created_search == False:
            new_search.chosen_datasource.add(ds)

        module_name = ".datasources." + ds.type + "." + ds.name + "_crawler"
        class_name = ds.name + "Crawler"
        module = importlib.import_module(module_name, package="crawler")
        class_ = getattr(module, class_name)

        if ds.type == "web":
            crawler = class_(unique_crawler_thread_id)
            crawler_threads.append(crawler)
            unique_crawler_thread_id = unique_crawler_thread_id + 1
            crawler.start()

        if ds.type == "custom":
            crawler = class_(unique_crawler_thread_id)
            crawler_threads.append(crawler)
            unique_crawler_thread_id = unique_crawler_thread_id + 1
            crawler.start()

        if ds.type == "socialnetwork":
            keywords_list = keywords.split(",")
            crawler = class_(unique_crawler_thread_id, keywords_list, ["1094299419556626432"])
            crawler_threads.append(crawler)
            unique_crawler_thread_id = unique_crawler_thread_id + 1
            crawler.start()


def create_search_threadid_list(len_selected_datasource):
    global unique_crawler_thread_id
    threadid_list = ""
    for i in range(0, len_selected_datasource):
        # 0, 1 , 2
        if (i == 0):
            threadid_list = str(unique_crawler_thread_id)
        else:
            threadid_list = threadid_list + "," + str(unique_crawler_thread_id + i)
    return threadid_list