from django.urls import path
from . import views

urlpatterns = [
    path("machines/<uuid:machine_id>/queue", views.queue_view, name="queue"),
    path(
        "machines/<uuid:machine_id>/queue/pause", views.queue_pause, name="queue-pause"
    ),
    path(
        "machines/<uuid:machine_id>/queue/resume",
        views.queue_resume,
        name="queue-resume",
    ),
    path(
        "machines/<uuid:machine_id>/queue/terminate",
        views.queue_terminate,
        name="queue-terminate",
    ),
    path("machines/<uuid:machine_id>/queue/skip", views.queue_skip, name="queue-skip"),
    path(
        "machines/<uuid:machine_id>/queue/items",
        views.queue_add_item,
        name="queue-items",
    ),
    path(
        "machines/<uuid:machine_id>/incoming_machine_telem",
        views.incoming_machine_telem,
        name="incoming-machine-state",
    ),
]
