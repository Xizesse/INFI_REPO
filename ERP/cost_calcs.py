from classes.order import Order
from classes.raw_order import Raw_order
from classes.PurchasingPlan import PurchasingPlan
from db import get_order, get_raw_orders, get_last_arrival_date

""""
def calculate_order_cost(order_id):

    order = get_order(order_id)
    purchasing_plan = get_purchasing_plan(order_id)

    prod_time = avg_prod_times[order.piece]

    dispatch_date = get_dispatch_date(order_id) 

    cost = order.calculate_costs(purchasing_plan, prod_time, dispatch_date, arrival_date)
    
    return cost

avg_prod_times = {
    "P5": 2.2,
    "P6": 2.2,
    "P7": 2.2,
    "P9": 2.2
}
"""
