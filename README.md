# Environment setup

Build the containers:

```
docker-compose up --build
```

Initialise and seed database:

```
docker-compose exec mower-queue python manage.py migrate
docker-compose exec mower-queue python manage.py seed_data
```

# API Endpoints

### 1. List queues

```
GET api/v1/machines/<uuid:machine_id>/queues
```

<details>
<summary>Request</summary>

```
docker compose exec mower-queue curl -X GET http://mower-queue:8000/api/v1/machines/051da667-809c-4694-b9cb-ac48002f3b72/queues
```

</details>
<details>
<summary>Response</summary>

```
{
    "data": [
        {
            "id": "ccab4624-4097-4269-9ff3-c7a5604c3e5c",
            "machine_id": "051da667-809c-4694-b9cb-ac48002f3b72",
            "status": "paused",
            "created_at": "2026-02-06T02:32:51.660032Z",
            "updated_at": "2026-02-06T02:32:51.660033Z",
            "items": [
                {
                    "id": "56528444-b8a0-4902-8439-f04943fca151",
                    "field_id": 19,
                    "position": 0,
                    "status": "completed",
                    "started_at": null,
                    "completed_at": null,
                    "created_at": "2026-02-06T02:32:51.671035Z"
                }
            ]
        }
    ],
}
```

</details>

### 2. Create queue

```
POST api/v1/machines/<uuid:machine_id>/queues
```

<details>
<summary>Request</summary>

```
docker compose exec mower-queue curl http://mower-queue:8000/api/v1/machines/051da667-809c-4694-b9cb-ac48002f3b72/queues -X POST -H "Content-Type: application/json" -d '{"field_ids": [1, 1, 2, 3]}'
```

</details>
<details>
<summary>Response</summary>

```
{
    "data": {
        "id": "69ef54e1-c662-46a4-8093-72ec379ce473",
        "machine_id": "051da667-809c-4694-b9cb-ac48002f3b72",
        "status": "active",
        "created_at": "2026-02-07T19:42:06.267887Z",
        "updated_at": "2026-02-07T19:42:06.267949Z",
        "items": [
            {
                "id": "9e7e6150-f185-4b4f-a228-2ef24f88fc17",
                "field_id": 1,
                "position": 0,
                "status": "pending",
                "started_at": null,
                "completed_at": null,
                "created_at": "2026-02-07T19:42:06.269283Z"
            },
            {
                "id": "97f1dfa6-a1d9-4ea4-b96b-f2f7026d1a94",
                "field_id": 1,
                "position": 1,
                "status": "pending",
                "started_at": null,
                "completed_at": null,
                "created_at": "2026-02-07T19:42:06.269300Z"
            },
            {
                "id": "edf3056f-1f14-47c8-b75d-9fe117352959",
                "field_id": 2,
                "position": 2,
                "status": "pending",
                "started_at": null,
                "completed_at": null,
                "created_at": "2026-02-07T19:42:06.269312Z"
            },
            {
                "id": "a4556b53-8316-412a-893a-1a262ab74d9c",
                "field_id": 3,
                "position": 3,
                "status": "pending",
                "started_at": null,
                "completed_at": null,
                "created_at": "2026-02-07T19:42:06.269323Z"
            }
        ]
    },
    "message": "Queue 69ef54e1-c662-46a4-8093-72ec379ce473 created successfully"
}
```

</details>

### 3. Start queue

```
POST api/v1/machines/<uuid:machine_id>/queues/<uuid:queue_id>/start
```

<details>
<summary>Request</summary>

```
docker compose exec mower-queue curl -X POST http://mower-queue:8000/api/v1/machines/051da667-809c-4694-b9cb-ac48002f3b72/queues/c56740fb-053d-4969-898b-3d282e8b33db/start
```

</details>
<details>
<summary>Response</summary>

```
{
    "data": {
        "id": "c56740fb-053d-4969-898b-3d282e8b33db",
        "machine_id": "051da667-809c-4694-b9cb-ac48002f3b72",
        "status": "active",
        "created_at": "2026-02-06T02:32:51.660006Z",
        "updated_at": "2026-02-07T17:05:18.109974Z",
        "items": [
            {
                "id": "4a870ed9-428d-4aa0-8e6e-b39c003d43bf",
                "field_id": 13,
                "position": 0,
                "status": "in_progress",
                "started_at": "2026-02-07T19:15:16.662017Z",
                "completed_at": null,
                "created_at": "2026-02-06T02:32:51.670685Z"
            },
            {
                "id": "a82dd95f-b118-46a3-a8fe-da1b21bd23ec",
                "field_id": 18,
                "position": 1,
                "status": "pending",
                "started_at": null,
                "completed_at": null,
                "created_at": "2026-02-06T02:32:51.670693Z"
            }
        ]
    },
    "message": "Queue started"
}
```

</details>

### 4. Pause queue

```
POST api/v1/machines/<uuid:machine_id>/queues/<uuid:queue_id>/pause
```

<details>
<summary>Request</summary>

```
docker compose exec mower-queue curl -X POST http://mower-queue:8000/api/v1/machines/051da667-809c-4694-b9cb-ac48002f3b72/queues/c56740fb-053d-4969-898b-3d282e8b33db/pause
```

</details>
<details>
<summary>Response</summary>

```
{
    "data": {
        "id": "c56740fb-053d-4969-898b-3d282e8b33db",
        "machine_id": "051da667-809c-4694-b9cb-ac48002f3b72",
        "status": "paused",
        "created_at": "2026-02-06T02:32:51.660006Z",
        "updated_at": "2026-02-07T19:20:17.420479Z",
        "items": [
            {
                "id": "4a870ed9-428d-4aa0-8e6e-b39c003d43bf",
                "field_id": 13,
                "position": 0,
                "status": "completed",
                "started_at": "2026-02-07T19:15:16.662017Z",
                "completed_at": "2026-02-07T19:15:47.051534Z",
                "created_at": "2026-02-06T02:32:51.670685Z"
            },
            {
                "id": "a82dd95f-b118-46a3-a8fe-da1b21bd23ec",
                "field_id": 18,
                "position": 1,
                "status": "in_progress",
                "started_at": "2026-02-07T19:15:47.051534Z",
                "completed_at": null,
                "created_at": "2026-02-06T02:32:51.670693Z"
            }
        ]
    },
    "message": "Queue paused"
}
```

</details>

### 5. Resume queue

```
POST api/v1/machines/<uuid:machine_id>/queues/<uuid:queue_id>/resume
```

<details>
<summary>Request</summary>

```
docker compose exec mower-queue curl -X POST http://mower-queue:8000/api/v1/machines/051da667-809c-4694-b9cb-ac48002f3b72/queues/c56740fb-053d-4969-898b-3d282e8b33db/resume
```

</details>
<details>
<summary>Response</summary>

```
{
    "data": {
        "id": "c56740fb-053d-4969-898b-3d282e8b33db",
        "machine_id": "051da667-809c-4694-b9cb-ac48002f3b72",
        "status": "active",
        "created_at": "2026-02-06T02:32:51.660006Z",
        "updated_at": "2026-02-07T19:20:17.420479Z",
        "items": [
            {
                "id": "4a870ed9-428d-4aa0-8e6e-b39c003d43bf",
                "field_id": 13,
                "position": 0,
                "status": "completed",
                "started_at": "2026-02-07T19:15:16.662017Z",
                "completed_at": "2026-02-07T19:15:47.051534Z",
                "created_at": "2026-02-06T02:32:51.670685Z"
            },
            {
                "id": "a82dd95f-b118-46a3-a8fe-da1b21bd23ec",
                "field_id": 18,
                "position": 1,
                "status": "in_progress",
                "started_at": "2026-02-07T19:15:47.051534Z",
                "completed_at": null,
                "created_at": "2026-02-06T02:32:51.670693Z"
            }
        ]
    },
    "message": "Queue resumed"
}
```

</details>

### 6. Terminate queue

```
POST api/v1/machines/<uuid:machine_id>/queues/<uuid:queue_id>/terminate
```

<details>
<summary>Request</summary>

```
docker compose exec mower-queue curl -X POST http://mower-queue:8000/api/v1/machines/051da667-809c-4694-b9cb-ac48002f3b72/queues/c56740fb-053d-4969-898b-3d282e8b33db/terminate
```

</details>
<details>
<summary>Response</summary>

```
{
    "data": {
        "id": "c56740fb-053d-4969-898b-3d282e8b33db",
        "machine_id": "051da667-809c-4694-b9cb-ac48002f3b72",
        "status": "terminated",
        "created_at": "2026-02-06T02:32:51.660006Z",
        "updated_at": "2026-02-07T19:20:17.420479Z",
        "items": [
            {
                "id": "4a870ed9-428d-4aa0-8e6e-b39c003d43bf",
                "field_id": 13,
                "position": 0,
                "status": "completed",
                "started_at": "2026-02-07T19:15:16.662017Z",
                "completed_at": "2026-02-07T19:15:47.051534Z",
                "created_at": "2026-02-06T02:32:51.670685Z"
            },
            {
                "id": "a82dd95f-b118-46a3-a8fe-da1b21bd23ec",
                "field_id": 18,
                "position": 1,
                "status": "in_progress",
                "started_at": "2026-02-07T19:15:47.051534Z",
                "completed_at": null,
                "created_at": "2026-02-06T02:32:51.670693Z"
            }
        ]
    },
    "message": "Queue terminated"
}
```

</details>

### 7. Skip current field

```
POST api/v1/machines/<uuid:machine_id>/queues/<uuid:queue_id>/skip
```

<details>
<summary>Request</summary>

```
docker compose exec mower-queue curl -X POST http://mower-queue:8000/api/v1/machines/051da667-809c-4694-b9cb-ac48002f3b72/queues/c56740fb-053d-4969-898b-3d282e8b33db/skip
```

</details>
<details>
<summary>Response</summary>

```
{
    "data": {
        "id": "c56740fb-053d-4969-898b-3d282e8b33db",
        "machine_id": "051da667-809c-4694-b9cb-ac48002f3b72",
        "status": "completed",
        "created_at": "2026-02-06T02:32:51.660006Z",
        "updated_at": "2026-02-07T19:20:17.420479Z",
        "items": [
            {
                "id": "4a870ed9-428d-4aa0-8e6e-b39c003d43bf",
                "field_id": 13,
                "position": 0,
                "status": "completed",
                "started_at": "2026-02-07T19:15:16.662017Z",
                "completed_at": "2026-02-07T19:15:47.051534Z",
                "created_at": "2026-02-06T02:32:51.670685Z"
            },
            {
                "id": "a82dd95f-b118-46a3-a8fe-da1b21bd23ec",
                "field_id": 18,
                "position": 1,
                "status": "skipped",
                "started_at": "2026-02-07T19:15:47.051534Z",
                "completed_at": null,
                "created_at": "2026-02-06T02:32:51.670693Z"
            }
        ]
    },
    "message": "Skipped field a82dd95f-b118-46a3-a8fe-da1b21bd23ec"
}
```

</details>

### 8. List queue items

```
GET api/v1/machines/<uuid:machine_id>/queues/<uuid:queue_id>/items
```

<details>
<summary>Request</summary>

```
docker compose exec mower-queue curl -X GET http://mower-queue:8000/api/v1/machines/051da667-809c-4694-b9cb-ac48002f3b72/queues/c56740fb-053d-4969-898b-3d282e8b33db/items
```

</details>
<details>
<summary>Response</summary>

```
{
    "data": [
        {
            "id": "4a870ed9-428d-4aa0-8e6e-b39c003d43bf",
            "field_id": 13,
            "position": 0,
            "status": "skipped",
            "started_at": "2026-02-07T19:26:32.260572Z",
            "completed_at": null,
            "created_at": "2026-02-06T02:32:51.670685Z"
        },
        {
            "id": "a82dd95f-b118-46a3-a8fe-da1b21bd23ec",
            "field_id": 18,
            "position": 1,
            "status": "in_progress",
            "started_at": "2026-02-07T19:26:46.435760Z",
            "completed_at": null,
            "created_at": "2026-02-06T02:32:51.670693Z"
        }
    ]
}
```

</details>

### 9. Add queue items

```
POST api/v1/machines/<uuid:machine_id>/queues/<uuid:queue_id>/items
```

<details>
<summary>Request</summary>

```
docker compose exec mower-queue curl -X POST http://mower-queue:8000/api/v1/machines/051da667-809c-4694-b9cb-ac48002f3b72/queues/c56740fb-053d-4969-898b-3d282e8b33db/items -H "Content-Type: application/json" -d '{"field_id": 9, "position": 2}'
```

</details>
<details>
<summary>Response</summary>

```
{
    "data": {
        "id": "398d0dc8-2a15-4fb8-8957-4b2311cbfd47",
        "field_id": 9,
        "position": 2,
        "status": "pending",
        "started_at": null,
        "completed_at": null,
        "created_at": "2026-02-07T19:33:35.110315Z"
    },
    "message": "Field 398d0dc8-2a15-4fb8-8957-4b2311cbfd47 added to queue"
}
```

</details>

### 10. Delete queue items

```
DELETE api/v1/machines/<uuid:machine_id>/queues/<uuid:queue_id>/items
```

<details>
<summary>Request</summary>

```
docker compose exec mower-queue curl -X DELETE http://mower-queue:8000/api/v1/machines/051da667-809c-4694-b9cb-ac48002f3b72/queues/c56740fb-053d-4969-898b-3d282e8b33db/items -H "Content-Type: application/json" -d '{"field_ids": ["398d0dc8-2a15-4fb8-8957-4b2311cbfd47"]}'
```

</details>
<details>
<summary>Response</summary>

```
{
    "message": "Fields deleted: ['398d0dc8-2a15-4fb8-8957-4b2311cbfd47']"
}
```

</details>
<br>

# Notes

- For this project, I assumed that a machine can have multiple queues (to ensure that a history of the data is kept)
- The machine is instructed to go to the next field when `incoming_machine_telem` indicates that the previous field was completed
