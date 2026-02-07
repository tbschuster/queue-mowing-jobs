import json
from urllib import request, error

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET", "POST"])
def queue_view(request, machine_id):
    """Handle queue GET and POST"""

    if request.method == "GET":
        # TODO: Implement get logic
        return Response({"queue_id": 1, "machine_id": machine_id, "status": "active"})

    elif request.method == "POST":
        # TODO: Implement create logic
        field_ids = request.data.get("field_ids", [])

        return Response(
            {
                "queue_id": 1,
                "machine_id": machine_id,
                "items": [
                    {"position": i, "field_id": fid} for i, fid in enumerate(field_ids)
                ],
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
def incoming_machine_telem(request, machine_id):
    """Handle state update from machine"""
    state = request.data.get("state")
    current_field = request.data.get("current_field")
    timestamp = request.data.get("timestamp")
    print(
        f"Incoming machine telem update State: {state}, Field: {current_field},"
        f" Timestamp: {timestamp}"
    )
    return Response({})


@api_view(["POST"])
def queue_pause(request, machine_id):
    """Pause queue"""
    # TODO: Implement pause logic
    return Response({"status": "paused", "message": "Queue paused"})


@api_view(["POST"])
def queue_resume(request, machine_id):
    """Resume queue"""
    # TODO: Implement resume logic
    return Response({"status": "active", "message": "Queue resumed"})


@api_view(["POST"])
def queue_terminate(request, machine_id):
    """Terminate queue"""
    # TODO: Implement terminate logic
    return Response({"status": "terminated", "message": "Queue terminated"})


@api_view(["POST"])
def queue_skip(request, machine_id):
    """Skip current field"""
    # TODO: Implement skip logic
    return Response({"message": "Field skipped"})


@api_view(["POST"])
def queue_add_item(request, machine_id):
    """Add field to queue"""
    # TODO: Implement add logic
    field_id = request.data.get("field_id")

    return Response({"message": "Field added to queue", "item": {"field_id": field_id}})


def send_machine_command():
    """Send command to machine"""
    try:
        payload = {
            "command": "start_mowing",
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
