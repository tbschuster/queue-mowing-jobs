from django.urls import path
from . import views

urlpatterns = [
    path(
        "machines/<uuid:machine_id>/queues",
        views.queue_view,
        name="queue",
    ),
    path(
        "machines/<uuid:machine_id>/queues/<uuid:queue_id>/start",
        views.queue_start,
        name="queue-start",
    ),
    path(
        "machines/<uuid:machine_id>/queues/<uuid:queue_id>/pause",
        views.queue_pause,
        name="queue-pause",
    ),
    path(
        "machines/<uuid:machine_id>/queues/<uuid:queue_id>/resume",
        views.queue_resume,
        name="queue-resume",
    ),
    path(
        "machines/<uuid:machine_id>/queues/<uuid:queue_id>/terminate",
        views.queue_terminate,
        name="queue-terminate",
    ),
    path(
        "machines/<uuid:machine_id>/queues/<uuid:queue_id>/skip",
        views.queue_skip,
        name="queue-skip",
    ),
    path(
        "machines/<uuid:machine_id>/queues/<uuid:queue_id>/items",
        views.queue_items,
        name="queue-items",
    ),
    path(
        "machines/<uuid:machine_id>/incoming_machine_telem",
        views.incoming_machine_telem,
        name="incoming-machine-state",
    ),
]
