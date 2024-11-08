from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F
import datetime
import pytz
import logging
from django.utils import timezone
import requests
import collections
from django.views import View
from .forms import UserForm
from .models import *
import statistics
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import matplotlib.pyplot as plt
from CarService import settings
import os
from django.db.models import Avg,Count,Sum,F
from django.contrib.sessions.backends.db import SessionStore

def calculate_age(birth_date):
    today = datetime.datetime.today() 
    age = today.year - birth_date.year 

    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1 

    return age

class MainView(View):
    def get(self, request):
        services = Service.objects.all()
        last_article = Article.objects.order_by("created_at").last()
        utc_now = datetime.datetime.now(tz=pytz.utc)
        return render(request, "main.html", {"services" : Service.objects.all(), "article" : last_article,
                                             "user_now": datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                                             "utc_now": utc_now.strftime('%d/%m/%Y %H:%M:%S'),
                                             "partners": Partner.objects.all(),
                                             "MEDIA_URL" : settings.MEDIA_URL,})

    def post(self, request):
        services = Service.objects.all()
        price_from = int(request.POST.get('price_from'))
        price_to = int(request.POST.get('price_to'))
        if price_from > price_to:
            return HttpResponse("Filter is not correct.")
        services = services.filter(price__gte=price_from)
        services = services.filter(price__lte=price_to)
        return render(request, "main.html", {"services" : services})
    
class ServicesView(View):
    def get(self, request):
        services = Service.objects.all()
        return render(request, "services.html", {"services" : Service.objects.all(),})

    def post(self, request):
        services = Service.objects.all()
        price_from = int(request.POST.get('price_from'))
        price_to = int(request.POST.get('price_to'))
        if price_from > price_to:
            return HttpResponse("Filter is not correct.")
        services = services.filter(price__gte=price_from)
        services = services.filter(price__lte=price_to)
        return render(request, "services.html", {"services" : services})

def statisticsv(request):
    clients = Client.objects.all()

    sum = 0
    years = []
    for cl in clients:
        age = datetime.date.today().year - cl.age.year
        years.append(age)
        sum += age
    avg_age = round(sum/len(years), 2)
    median_age = statistics.median(years)

    sum = 0
    sale_prices = []
    for cl in clients:
        sum += cl.result_price
        sale_prices.append(cl.result_price)
    avg_sale_price = round(sum/len(clients), 2)
    median_sale_price = statistics.median(sale_prices)
    mode_sale_price = statistics.mode(sale_prices)

    alphabet_clients = Client.objects.order_by("name")
    whole_sale_price = round(sum, 2)

    orders = Order.objects.all()

    order_services = []
    for o in orders:
        order_services.append(o.service)
    print(order_services)
    service_counts = collections.Counter(order_services)
    most_common_service = max(service_counts, key=service_counts.get)
    sales_distribution_chart()


    return render(request, "statistics.html", {"average_age" : avg_age,
                                               "median_age" : median_age,
                                               "average_sale_price" : avg_sale_price,
                                               "median_sale_price" : median_sale_price,
                                               "mode_sale_price" : mode_sale_price,
                                               "sorted_clients" : alphabet_clients,
                                               "whole_sale_price" : whole_sale_price,
                                               "most_common_service" : most_common_service,
                                               "MEDIA_URL" : settings.MEDIA_URL,})


def most_common_service():
    orders = Order.objects.all()

    order_services = []
    for o in orders:
        order_services.append(o.service)
    service_counts = collections.Counter(order_services)
    most_common_service = max(service_counts, key=service_counts.get)
    return most_common_service

def get_sales_by_product_type():
    sales_by_product_type = Order.objects.values('service').annotate(
        total_sales=Count('id'))
    
    return sales_by_product_type

def sales_distribution_chart():

    sales_data = get_sales_by_product_type()
    types = [sale['service'] for sale in sales_data]
    total_sales = [sale['total_sales'] for sale in sales_data]

    plt.figure(figsize=(8, 6))
    plt.pie(total_sales, labels=types, autopct='%1.1f%%')
    plt.title('Распределение продаж по типам товаров')
    plt.axis('equal') 
    save_path = os.path.join(settings.MEDIA_ROOT, 'sales_distribution_chart.png')
    plt.savefig(save_path)

def about_company(request):
    return render(request, "about_company.html")

def contacts(request):
    masters = Master.objects.all()
    ages = []
    for m in masters:
        age = calculate_age(m.age)
        ages.append(age)
    masters_with_ages = zip(masters, ages)
    return render(request, "contacts.html", {"masters" : masters,
                                             "ages": ages,
                                             "masters_with_ages": masters_with_ages,
                                             "MEDIA_URL" : settings.MEDIA_URL,})

#сортировка
def news(request):
    artcs = Article.objects.all()
    if request.method == "POST":
        val = request.POST.get("sort")
        if val == "date_new":
            artcs = Article.objects.order_by("created_at").reverse()
        elif val == "date_old":
            artcs = Article.objects.order_by("created_at")
        return render(request, "news.html", {"articles" : artcs,})
    return render(request, "news.html", {"articles" : artcs,
                                         "MEDIA_URL" : settings.MEDIA_URL,})

def article(request, art_id):
    art = Article.objects.get(id=art_id)
    return render(request, "article.html", 
                  {"article" : art,
                   "MEDIA_URL" : settings.MEDIA_URL,})

def politics(request):
    return render(request, "politics.html")

#поиск
def promocodes(request):
    proms = Promocode.objects.all()
    sprom = None
    if request.method == "POST":
        tname = request.POST.get("search_term")
        if Promocode.objects.filter(name = tname).exists():
            sprom = Promocode.objects.filter(name = tname)
            return render(request, "promocodes.html", {"proms" : proms, "searched" : sprom,})
    return render(request, "promocodes.html", {"proms" : proms, "searched" : sprom,})

def qa(request):
    qas = QA.objects.all()
    return render(request, "qa.html", {"qas" : qas,})

def detail_qa(request, id):
    qa = get_object_or_404(QA, id=id)
    return render(request, 'detail_qa.html', {'qa': qa})

def reviews(request):
    if request.method == "POST":
        return render(request, "register.html", {'specializations' : Specialization.objects.all(),})
    return render(request, "reviews.html", {"reviews" : Review.objects.order_by("date").reverse(),})

def vacancies(request):
    return render(request, "vacancies.html", {"jobs" : Job.objects.all(),})

def login(request):
    userform = UserForm()
    if request.method == "POST":
        userform = UserForm(request.POST)
        if not userform.is_valid():
            tlogin = request.POST.get("login")
            tpassword = request.POST.get("password")
            usertype = request.POST.get("user_type")
            
            if usertype == "master":
                searched_masters = MasterCredentials.objects.filter(login=tlogin)
                if searched_masters.exists():
                    searched_masters = searched_masters.filter(password=tpassword)
                    if searched_masters.exists():
                        master = searched_masters.first().master
                        request.session['user_id'] = master.id
                        request.session['user_type'] = 'master'
                        logging.info(f"Master {master.name} added.")
                        return redirect(f'master/{master.pk}')
                    else:
                        logging.warning("Invalid password for master.")
                        return HttpResponseNotFound("Invalid password")
                else:
                    logging.warning("No master with this login found.")
                    return HttpResponseNotFound("No master with this login found")
            else:
                searched_clients = ClientCredentials.objects.filter(login=tlogin)
                if searched_clients.exists():
                    searched_clients = searched_clients.filter(password=tpassword)
                    if searched_clients.exists():
                        client = searched_clients.first().client
                        request.session['user_id'] = client.id
                        request.session['user_type'] = 'client'
                        logging.info(f"Client {client.name} added.")
                        return redirect(f'client/{client.pk}')
                    else:
                        logging.warning("Invalid password for client.")
                        return HttpResponseNotFound("Invalid password")
                else:
                    logging.warning("No client with this login found.")
                    return HttpResponseNotFound("No client with this login found")
        else:
            return HttpResponse("Invalid data")
    else:
        return render(request, "login.html", {"form": userform})


def CheckAge(age):
    min_birthday = datetime.date.today() - datetime.timedelta(days=365*18)
    if min_birthday < age:
        return False
    return True


def register(request):
    userform = UserForm()
    if request.method == "POST":
        userform = UserForm(request.POST)
        if userform.is_valid():
            tpassword = request.POST.get("password")
            tlogin = request.POST.get("login")
            name = request.POST.get("name")
            age = request.POST.get("date_of_birth")
            tphone_number = "+375 (" + request.POST.get("phone_code") + ") " + request.POST.get("phone_number")
            usertype = request.POST.get("user_type")

            dob = datetime.datetime.strptime(age, "%Y-%m-%d").date()

            is_adult = CheckAge(dob)
            if is_adult == False:
                return HttpResponse("You must be 18+ y/o.")
            
            if usertype == "master":
                if MasterCredentials.objects.filter(login = tlogin).exists():
                    return HttpResponse("Master with this login already exists.")
                new_master = Master()
                new_master.name = name
                new_master.age = age
                new_master.phone_number = tphone_number
                new_master.order_count = 0
                new_master.specialization = Specialization.objects.first()
                new_master.save()
                new_master_cred = MasterCredentials()
                new_master_cred.master = new_master
                new_master_cred.login = tlogin
                new_master_cred.password = tpassword
                new_master_cred.save()
                return redirect(f'master/{new_master.pk}')
            else:
                if ClientCredentials.objects.filter(login = tlogin).exists():
                    return HttpResponse("Client with this login already exists.")
                new_client = Client()
                new_client.name = name
                new_client.age = age
                new_client.phone_number = tphone_number
                new_client.result_price = 0
                new_client.car_model = CarModel.objects.first()
                new_client.car_type = CarType.objects.first()
                new_client.save()
                new_cl_creds = ClientCredentials()
                new_cl_creds.client = new_client
                new_cl_creds.login = tlogin
                new_cl_creds.password = tpassword
                new_cl_creds.save()
                return redirect(f'client/{new_client.pk}')
        else:
            return HttpResponse("Invalid data")
    else:
        return render(request, "register.html", {'specializations' : Specialization.objects.all(),
                                                 "form" : userform})
    
    

def mastersview(request, master_id):
    mast = Master.objects.get(id = master_id)
    clients_id = ClientMaster.objects.filter(master = mast)
    clients = set(cm.client for cm in clients_id)
    return render(request, "master.html", {"master": mast, "master_id" : master_id, "specs" : Specialization.objects.all(),
                                           "orders" : Order.objects.filter(master = mast),
                                           "clients" : clients})

def clientsview(request, client_id):
    client = Client.objects.get(id = client_id)
    return render(request, "client.html", {"client": client, 
                                           "client_id" : client_id, 
                                           "car_models" : CarModel.objects.all(), 
                                           "car_types" : CarType.objects.all(),
                                           "proms" : Promocode.objects.all(),
                                           "reviews" : Review.objects.filter(user = client).order_by("date").reverse()})


def editmaster(request, master_id):
    mast = Master.objects.get(id = master_id)
    if request.method == "POST":
        tname = request.POST.get("name")
        tage = request.POST.get("age")
        tphone_number = "+375 (" + request.POST.get("phone_code") + ") " + request.POST.get("phone_number")
        tspecialization = request.POST.get("specialization")
        tphoto = request.POST.get("photo")
        Master.objects.filter(id = master_id).update(name=tname,age=tage,phone_number=tphone_number,specialization=tspecialization,img_url=tphoto)
        mast = Master.objects.get(id = master_id)
        return redirect('master',master_id=master_id)
    return render(request, "editmaster.html", {"master": mast, "specs" : Specialization.objects.all()})

def editclient(request, client_id):
    client = Client.objects.get(id = client_id)
    if request.method == "POST":
        tname = request.POST.get("name")
        tage = request.POST.get("age")
        tphone_number = "+375 (" + request.POST.get("phone_code") + ") " + request.POST.get("phone_number")
        tmodel = request.POST.get("model_car")
        ttype = request.POST.get("type_car")
        Client.objects.filter(id = client_id).update(name=tname, age=tage, phone_number=tphone_number, car_model=tmodel, car_type=ttype)
        client = Client.objects.get(id = client_id)
        return redirect('client',client_id = client_id)
    else:
        return render(request, "editclient.html", {"client": client, "car_models" : CarModel.objects.all(), "car_types" : CarType.objects.all()})
    

def createorder(request, client_id):
    client = Client.objects.get(id = client_id)
    if request.method == "POST":
        order = Order()
        order.master = Master.objects.get(id = request.POST.get("master"))
        order.client = client
        order.ordering_time = datetime.datetime.now()
        order.service = Service.objects.get(id = request.POST.get("service"))
        selected_parts = Part.objects.filter(id__in=request.POST.getlist("parts"))
        prom = None
        if request.POST.get("promocode"):
            try:
                prom = Promocode.objects.get(name = request.POST.get("promocode"))
            except:
                prom = None
        if prom is None:
            order.whole_price = order.CountPrice(parts=selected_parts)
        else:
            order.whole_price = order.CountPrice(prom,selected_parts)
        order.save()
        Client.objects.filter(id = client_id).update(result_price=F('result_price') + order.whole_price)
        Master.objects.filter(id = order.master.pk).update(order_count=F('order_count') + 1)
        master = Master.objects.get(id = order.master.pk)
        client = Client.objects.get(id = client_id)
        new_clientmaster = ClientMaster()
        new_clientmaster.client = client
        new_clientmaster.master = master
        new_clientmaster.save()
        return redirect('client',client_id = client.pk)
    else:
        return render(request,"createorder.html", {"client_id" : client_id, 
                                                   "masters" : Master.objects.all(), 
                                                   "services" : Service.objects.all(), 
                                                   "parts" : Part.objects.filter(car_model = client.car_model)})
    
@login_required
def createreview(request, client_id):
    user = Client.objects.get(id = client_id)
    if request.method == "POST":
        ttext = request.POST.get("text")
        trating = request.POST.get("rating")
        new_review = Review()
        new_review.user = user
        new_review.text = ttext
        new_review.rating = int(trating)
        new_review.save()
        return redirect('client',client_id = user.pk)
    else:
        return render(request,"createreview.html")

@login_required    
def editreview(request, client_id, review_id):
    user = Client.objects.get(id = client_id)
    review = Review.objects.get(id = review_id)
    if request.method == "POST":
        ttext = request.POST.get("text")
        trating = request.POST.get("rating")

        Review.objects.filter(id = review_id).update(text = ttext)
        Review.objects.filter(id = review_id).update(rating = int(trating))
        return redirect('client',client_id = user.pk)
    else:
        return render(request,"editreview.html", {"review" : review})

@login_required    
def deletereview(request, client_id, review_id):
    user = Client.objects.get(id = client_id)
    review = Review.objects.get(id = review_id)
    if request.method == "POST":
        review.delete()
        return redirect('client',client_id = user.pk)
    else:
        return render(request,"deletereview.html", {"review" : review})
    
def cart_detail(request):
    cart = Cart.objects.first() 
    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items:
        total_price = 0
    else:
        total_price = sum(item.service.price * item.quantity for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

    
def add_to_cart(request, service_id):
    cart = Cart.objects.first()
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Проверяем, есть ли элементы в корзине
    if not cart_items:
        total_price = 0
    else:
        total_price = sum(item.service.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        service = get_object_or_404(Service, id=service_id)
        item, created = CartItem.objects.get_or_create(cart=cart, service=service)
        if not created:
            # Если товар уже есть в корзине, увеличиваем его количество
            item.quantity += 1
            item.save()

        return redirect('add_to_cart', service_id=service.id)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

def update_cart_item(request, item_id, service_id):
    item = get_object_or_404(CartItem, id=item_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increase':
            item.quantity += 1
            item.save()
        elif action == 'decrease' and item.quantity > 1:
            item.quantity -= 1
            item.save()
        elif action == 'remove':
            item.delete()
    
    return redirect('add_to_cart', service_id=service_id)

    
class ServiceDetailView(View):
    def get(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        return render(request, 'servicedetail.html', {'service': service})

class CheckoutView(View):
    def get(self, request):
        return render(request, 'checkout.html')

    def post(self, request):
        #####
        return redirect('main')
    



    
