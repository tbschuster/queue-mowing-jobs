import random

from django.core.management.base import BaseCommand
from django_seed import Seed

from ...models import Machine, FieldQueue, FieldQueueItem


class Command(BaseCommand):
    """Command to seed the database with random data"""

    help = "Seeds the database with random data"

    def handle(self, *args, **kwargs):

        machines_with_active_queues = set()

        def get_queue_status(machine_id):
            status = random.choices(
                ["active", "paused", "terminated", "completed"],
                weights=[0.5, 0.2, 0.1, 0.2],
                k=1,
            )[0]
            if status == "active" and machine_id in machines_with_active_queues:
                # We assume that there's only one active queue per machine
                status = random.choices(
                    ["paused", "terminated", "completed"],
                    weights=[0.3, 0.2, 0.5],
                    k=1,
                )[0]
            elif status == "active":
                machines_with_active_queues.add(machine_id)
            return status

        seeder = Seed.seeder()
        seeder.add_entity(
            Machine,
            10,
            {
                "name": lambda x: f"Machine {seeder.faker.unique.last_name()}",
            },
        )
        seeder.execute()
        print(self.style.SUCCESS("Machines seeded."))

        field_queues = []
        for _ in range(100):
            machine = Machine.objects.order_by("?").first()
            field_queues.append(
                FieldQueue(
                    machine=machine,
                    status=get_queue_status(machine.id),
                )
            )
        FieldQueue.objects.bulk_create(field_queues)
        print(self.style.SUCCESS("Field queues seeded."))

        queue_items = []
        for queue in FieldQueue.objects.all():
            has_reached_in_progress = False
            for idx in range(0, seeder.faker.random_int(min=0, max=10)):
                if queue.status == "completed":
                    possible_statuses = ["completed", "skipped"]
                    weights = [0.8, 0.2]
                elif not has_reached_in_progress:
                    possible_statuses = ["in_progress", "completed", "skipped"]
                    weights = [0.6, 0.3, 0.1]
                else:
                    possible_statuses = ["pending"]
                    weights = [1]

                status = random.choices(
                    possible_statuses,
                    weights=weights,
                    k=1,
                )[0]

                if status == "in_progress":
                    has_reached_in_progress = True

                queue_items.append(
                    FieldQueueItem(
                        queue=queue,
                        field_id=seeder.faker.random_int(min=1, max=20),
                        position=idx,
                        status=status,
                    )
                )

        FieldQueueItem.objects.bulk_create(queue_items)
        print(self.style.SUCCESS("Queue items seeded."))
