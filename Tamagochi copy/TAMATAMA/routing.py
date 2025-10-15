from django.urls import re_path
from TAMATAMA.consumers import tam_need_water, tam_need_food, tam_need_sleep, tam_need_playtime, tam_parameter_income, class_chat


websocket_urlpatterns = [
    re_path(r"ws/tam_water/$", tam_need_water.as_asgi()),
    re_path(r"ws/tam_food/$", tam_need_food.as_asgi()),
    re_path(r"ws/tam_sleep/$", tam_need_sleep.as_asgi()),
    re_path(r"ws/tam_playtime/$", tam_need_playtime.as_asgi()),
    re_path(r"ws/tam_income/$", tam_parameter_income.as_asgi()),
    re_path(r"ws/global_chat/$", class_chat.as_asgi()),
]