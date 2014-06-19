from order.models import Order, OrderNote


class OrderHelper(object):
    """
    Places the order
    """
    @classmethod
    def place_order(cls, user=None, **fields):
        order_data = {
            "type": "DEFAULT",
            "status": "New",
        }

        order = Order(**order_data)
        order.extra_data = fields
        order.save()

        cls._create_order_note(order, user, **fields)
        return order

    @classmethod
    def update_order(cls, order, user=None, **fields):
        order.extra_data = fields
        if 'type' in fields:
            order.type = fields['type']
        if 'status' in fields:
            order.status = fields['status']

        order.save()

        cls._create_order_note(order, user, **fields)

        return order

    @classmethod
    def _create_order_note(cls, order, user, **fields):
        order_note = OrderNote()
        order_note.type = order.type
        order_note.order = order
        order_note.extra_data = fields

        if user:
            order_note.user = user

        if 'message' in fields:
            order_note.message = fields['message']

        order_note.save()
        return order_note
