from django.dispatch import Signal

signal_user_registered = Signal(providing_args=[])
signal_product_bought = Signal(providing_args=[])
signal_product_first_bought = Signal(providing_args=['user'])