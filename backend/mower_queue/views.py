import json
from urllib import request, error

from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Machine, FieldQueue


@api_view(["GET", "POST"])
def queue_view(request, machine_id):
    """Handle machine queues GET and POST"""
    try:
        machine = Machine.objects.get(id=machine_id)
    except Machine.DoesNotExist:
        return Response(
            {
                "message": f"Machine {machine_id} does not exist.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "GET":
        queues = FieldQueue.objects.filter(machine_id=machine_id)
        return Response({"data": [queue.serialize() for queue in queues]})

    elif request.method == "POST":
        field_ids = request.data.get("field_ids", [])

        if len(field_ids) > 10:
            return Response(
                {
                    "message": "A queue may only have 10 queued items.",
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        queue = machine.add_queue(field_ids=field_ids)
        return Response(
            {
                "data": queue.serialize(),
                "message": f"Queue {queue.id} created successfully",
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
def incoming_machine_telem(request, machine_id):
    """Handle state update from machine"""
    state = request.data.get("state").lower()
    current_queue_id = request.data.get("current_queue")
    current_field_id = request.data.get("current_field")
    previous_field_id = request.data.get("previous_field")
    timestamp = request.data.get("timestamp")
    print(
        f"Incoming machine telem update State: {state}, Field: {current_field_id},"
        f" Timestamp: {timestamp}"
    )

    if state in ["paused", "mowing"]:
        # No action required
        return Response({"message": "No action required"})

    elif state == "idle" and not current_field_id and current_queue_id:
        # The machine has finished the previous task and might need further instructions
        try:
            queue = FieldQueue.objects.get(
                id=current_queue_id,
                machine_id=machine_id,
            )
        except FieldQueue.DoesNotExist:
            return Response(
                {
                    "message": (
                        f"Queue {current_queue_id} does not exist on machine"
                        f" {machine_id}."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        next_item = queue.next_item(
            timestamp=timestamp,
            previous_item_id=previous_field_id,
        )
        queue.refresh_from_db()

        if next_item and queue.status == "active":
            send_machine_command(
                command="start_mowing",
                field_id=next_item.id,
                queue_id=current_queue_id,
            )
            Response(
                {
                    "data": queue.serialize(),
                    "message": (
                        f"Machine {machine_id} can start mowing field {next_item.id}"
                    ),
                }
            )
    return Response({"message": "No action required"})


@api_view(["POST"])
def queue_start(request, machine_id, queue_id):
    """Start queue"""
    try:
        field_queue = FieldQueue.objects.get(
            id=queue_id,
            machine_id=machine_id,
        )
    except FieldQueue.DoesNotExist:
        return Response(
            {
                "message": f"Queue {queue_id} does not exist on machine {machine_id}.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    return start_queue(field_queue)


def start_queue(queue):
    queue.update_status("active")
    if item := queue.next_item():
        queue.refresh_from_db()
        send_machine_command(
            command="start_mowing",
            field_id=item.id,
            queue_id=queue.id,
        )

        return Response(
            {
                "data": queue.serialize(),
                "message": "Queue started",
            }
        )
    return Response(
        {
            "message": f"No items left in queue {queue.id}",
        },
        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


@api_view(["POST"])
def queue_pause(request, machine_id, queue_id):
    """Pause queue"""
    try:
        queue = FieldQueue.objects.get(
            id=queue_id,
            machine_id=machine_id,
        )
    except FieldQueue.DoesNotExist:
        return Response(
            {
                "message": f"Queue {queue_id} does not exist on machine {machine_id}.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    queue.update_status("paused")

    send_machine_command(
        command="pause",
        queue_id=queue_id,
    )

    return Response(
        {
            "data": queue.serialize(),
            "message": "Queue paused",
        }
    )


@api_view(["POST"])
def queue_resume(request, machine_id, queue_id):
    """Resume queue"""
    try:
        queue = FieldQueue.objects.get(
            id=queue_id,
            machine_id=machine_id,
        )
    except FieldQueue.DoesNotExist:
        return Response(
            {
                "message": f"Queue {queue_id} does not exist on machine {machine_id}.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if queue.status == "terminated":
        return start_queue(queue)

    queue.update_status("active")

    send_machine_command(
        command="resume",
        queue_id=queue_id,
    )

    return Response(
        {
            "data": queue.serialize(),
            "message": "Queue resumed",
        }
    )


@api_view(["POST"])
def queue_terminate(request, machine_id, queue_id):
    """Terminate queue"""
    try:
        queue = FieldQueue.objects.get(
            id=queue_id,
            machine_id=machine_id,
        )
    except FieldQueue.DoesNotExist:
        return Response(
            {
                "message": f"Queue {queue_id} does not exist on machine {machine_id}.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    queue.update_status("terminated")

    send_machine_command(
        command="stop",
        queue_id=queue_id,
    )

    return Response(
        {
            "data": queue.serialize(),
            "message": "Queue terminated",
        }
    )


@api_view(["POST"])
def queue_skip(request, machine_id, queue_id):
    """Skip current field"""
    try:
        queue = FieldQueue.objects.get(
            id=queue_id,
            machine_id=machine_id,
        )
    except FieldQueue.DoesNotExist:
        return Response(
            {
                "message": (
                    f"Failed to skip field. Queue {queue_id} does not exist on machine"
                    f" {machine_id}."
                )
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    item = queue.items.filter(status="in_progress").order_by("position").first()
    if not item:
        return Response(
            {"message": f"No fields can be skipped on queue {queue_id}"},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    item.status = "skipped"
    item.save()

    if queue.status in ["active", "paused"]:
        next_item = queue.next_item()
        queue.refresh_from_db()
        send_machine_command(
            "update_current_field",
            field_id=next_item.id if next_item else "",
            queue_id=queue_id,
        )
    return Response(
        {
            "data": queue.serialize(),
            "message": f"Skipped field {item.id}",
        }
    )


@api_view(["GET", "POST", "DELETE"])
def queue_items(request, machine_id, queue_id):
    """Add field to queue"""
    try:
        queue = FieldQueue.objects.get(
            id=queue_id,
            machine_id=machine_id,
        )
    except FieldQueue.DoesNotExist:
        return Response(
            {
                "message": (
                    f"Failed to add field. Queue {queue_id} does not exist on"
                    f" machine {machine_id}."
                )
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "GET":
        return Response(
            {
                "data": [x.serialize() for x in queue.items.all()],
            }
        )

    elif request.method == "POST":
        position = request.data.get("position")

        if not (field_id := request.data.get("field_id")):
            return Response(
                {"message": "Missing field id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            new_item = queue.add_item(field_id=field_id, position=position)
        except ValidationError as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return Response(
            {
                "data": new_item.serialize(),
                "message": f"Field {new_item.id} added to queue",
            },
            status=status.HTTP_201_CREATED,
        )

    elif request.method == "DELETE":
        if not (fields := request.data.get("field_ids", [])):
            return Response(
                {"message": "Missing fields"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            queue.remove_items(fields)
        except ValidationError as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        return Response(
            {
                "message": f"Fields deleted: {fields}",
            }
        )


def send_machine_command(command, field_id="", queue_id=""):
    """Send command to machine"""
    try:
        payload = {
            "command": command,
            "field_id": str(field_id),
            "queue_id": str(queue_id),
        }
        # Convert payload to JSON bytes
        json_data = json.dumps(payload).encode("utf-8")

        # Create request
        url = "http://machine-simulator:5001/command"
        req = request.Request(
            url,
            data=json_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        # Send request
        with request.urlopen(req, timeout=5) as response:
            print(f"Sending command to machine, payload: {json_data}")
            response_data = response.read().decode("utf-8")

    except error.HTTPError as e:
        print(f"[Unable to send machine command] HTTP Error {e.code}: {e.reason}")
    except error.URLError as e:
        print(f"[Unable to send machine command] URL Error: {e.reason}")
