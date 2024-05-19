from decimal import Decimal

from pizza_delivery.models import Order, DishOrder


def get_user_orders(request):
    session_key = request.session.session_key
    customer = request.user

    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    if customer.is_authenticated:
        orders = Order.objects.filter(customer=customer, status="created")
    else:
        orders = Order.objects.filter(
            session_key=session_key, status="created"
        )

    order_items = []
    total_price = Decimal("0.00")
    for order in orders:
        dish_orders = DishOrder.objects.filter(order=order)
        for dish_order in dish_orders:
            total_price += dish_order.dish.price * dish_order.dish_amount
            order_items.append(
                {
                    "dish_name": dish_order.dish.name,
                    "dish_amount": dish_order.dish_amount,
                    "dish_price": (dish_order.dish.price
                                   * dish_order.dish_amount),
                }
            )

    return {"order_items": order_items, "total_price": total_price}


def get_orders_for_customer_or_session(request):
    customer = request.user
    session_key = request.session.session_key

    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    if customer.is_authenticated:
        return Order.objects.filter(customer=customer, status="created")
    else:
        return Order.objects.filter(session_key=session_key, status="created")
