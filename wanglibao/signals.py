from django.dispatch import Signal

user_registered = Signal(providing_args=[])
product_bought = Signal(providing_args=[])
product_first_bought = Signal(providing_args=[])