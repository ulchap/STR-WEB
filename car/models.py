from django.db import models
from django.utils.timezone import now

class ServiceType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Service(models.Model):
    name = models.CharField(max_length=50)
    price = models.PositiveIntegerField()
    category = models.ForeignKey(ServiceType, related_name="services", on_delete=models.CASCADE)
    img = models.ImageField(upload_to='images/services', default='images/services/service1.png')

    def __str__(self):
        return self.name


class CarModel(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class CarType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Specialization(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    

class Client(models.Model):
    name = models.CharField(max_length=30)
    age = models.DateField()
    phone_number = models.CharField(max_length=19)
    result_price = models.PositiveIntegerField()
    car_model = models.ForeignKey(CarModel, related_name="clients", on_delete=models.DO_NOTHING)
    car_type = models.ForeignKey(CarType, related_name="clients", on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name

class Master(models.Model):
    name = models.CharField(max_length=30)
    age = models.DateField()
    phone_number = models.CharField(max_length=19)
    specialization = models.ForeignKey(Specialization, related_name="masters", on_delete=models.CASCADE,  default=None)
    order_count = models.PositiveIntegerField()
    img = models.ImageField(upload_to='images/masters', default='images/services/service1.png')

    def __str__(self):
        return self.name


class ClientCredentials(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, primary_key=True)
    login = models.CharField(max_length=20, default="login")
    password = models.CharField(max_length=20, default="password")


class MasterCredentials(models.Model):
    master = models.OneToOneField(Master, on_delete=models.CASCADE, primary_key=True)
    login = models.CharField(max_length=20, default="login")
    password = models.CharField(max_length=20, default="password")

class PartType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Part(models.Model):
    name = models.CharField(max_length=20)
    car_model = models.ForeignKey(CarModel, related_name="parts", on_delete=models.CASCADE, default=None)
    price = models.PositiveIntegerField()
    type = models.ForeignKey(PartType, related_name="parts", on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.name

class Promocode(models.Model):
    name = models.CharField(max_length=15)
    discount = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name

class Order(models.Model):
    master = models.ForeignKey(Master, related_name="orders", on_delete=models.CASCADE, default=None)
    client = models.ForeignKey(Client, related_name="orders", on_delete=models.CASCADE, default=None)
    whole_price = models.PositiveIntegerField()
    ordering_time = models.DateTimeField()
    service = models.ForeignKey(Service, related_name="orders", on_delete=models.DO_NOTHING)

    def CountPrice(self, prom = None, parts = None):
        price = self.service.price
        if parts:
            for p in parts:
                price += p.price
        if prom:
            price *= 0.01*(100-prom.discount)
        return price


class ClientMaster(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    master = models.ForeignKey(Master, on_delete=models.CASCADE)

class QA(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    date = models.DateField(default=now)


class Job(models.Model):
    title = models.CharField(max_length=50)
    salary = models.IntegerField()
    description = models.TextField()

class Review(models.Model):
    user = models.ForeignKey(Client, on_delete=models.DO_NOTHING)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveSmallIntegerField(default=5)


class Article(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    img_url = models.ImageField(upload_to='images/articles')
    created_at = models.DateTimeField(auto_now_add=True)

class Partner(models.Model):
    name = models.CharField(max_length=50)
    site_url = models.CharField(max_length=200,default='')
    logo_url = models.ImageField(upload_to='images')

class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
