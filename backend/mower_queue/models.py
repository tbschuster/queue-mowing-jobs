import uuid
from datetime import datetime

from django.db import models, transaction
from django.utils import timezone
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError


class Machine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)

    def add_queue(self, field_ids):
        with transaction.atomic():
            queue = FieldQueue(machine=self)
            queue.save()

            now = timezone.now()
            FieldQueueItem.objects.bulk_create(
                [
                    FieldQueueItem(
                        queue=queue,
                        field_id=field_id,
                        position=i,
                        created_at=now,
                    )
                    for i, field_id in enumerate(field_ids)
                ]
            )
            return queue


class FieldQueue(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("paused", "Paused"),
        ("terminated", "Terminated"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        related_name="queues",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def serialize(self):
        """Serialize field queue instance"""
        return {
            "id": self.id,
            "machine_id": self.machine.id,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "items": [x.serialize() for x in self.items.all()],
        }

    def update_status(self, status):
        if self.status != status:
            self.status = status
            self.save()

    def add_item(self, field_id, position=None):
        """Add new item to the queue"""
        with transaction.atomic():
            queue = FieldQueue.objects.select_for_update().get(id=self.id)
            item_count = queue.items.count()
            position = item_count if position is None else position

            if position < 0:
                raise ValidationError(
                    f"Failed to add field to queue {queue.id}. Position {position} is"
                    " out of range."
                )

            if position >= 10 or item_count >= 10:
                raise ValidationError(
                    f"Failed to add field to queue {queue.id}. The queue has reached"
                    " the maximum amount of 10 queued items."
                )

            if position > item_count + 1 or (item_count == 0 and position != 0):
                raise ValidationError(
                    f"Failed to add field  to queue {queue.id} at position {position}."
                    f" The queue only has {item_count} queued items."
                )

            queue.items.filter(position__gte=position).update(
                position=models.F("position") + 1
            )

            new_item = FieldQueueItem(
                queue=queue,
                field_id=field_id,
                position=position,
            )
            new_item.save()

            return new_item

    def next_item(self, timestamp=None, previous_item_id=None):
        timestamp = datetime.fromtimestamp(timestamp) if timestamp else timezone.now()
        with transaction.atomic():
            queue = FieldQueue.objects.select_for_update().get(id=self.id)

            if previous_item_id:
                try:
                    previous = queue.items.select_for_update().get(id=previous_item_id)
                except FieldQueueItem.DoesNotExist:
                    previous = None

                if previous and previous.status not in ["completed", "skipped"]:
                    previous.status = "completed"
                    previous.completed_at = timestamp
                    previous.save()

            next_item = (
                queue.items.select_for_update()
                .filter(status__in=["pending", "in_progress"])
                .order_by("position")
                .first()
            )

            if next_item:
                if next_item.status != "in_progress":
                    next_item.status = "in_progress"
                    next_item.started_at = timestamp
                    next_item.save()
                return next_item

            # No more items in the queue
            queue.status = "completed"
            queue.save()

    def remove_items(self, field_ids):
        possible_fields = [str(x.id) for x in self.items.all()]
        if err_fields := [x for x in field_ids if x not in possible_fields]:
            # Make sure that the fields are part of the queue
            raise ValidationError(
                f"The following fields are not part of the {self.id} queue:"
                f" {err_fields}"
            )

        with transaction.atomic():
            FieldQueueItem.objects.filter(id__in=field_ids).delete()
            queue = FieldQueue.objects.select_for_update().get(id=self.id)

            # Update positions in the queue
            for i, field in enumerate(queue.items.order_by("position")):
                if field.position != i:
                    field.position = i
                    field.save()


class FieldQueueItem(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("skipped", "Skipped"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    queue = models.ForeignKey(
        FieldQueue, on_delete=models.CASCADE, related_name="items"
    )
    field_id = models.IntegerField()
    position = models.IntegerField(validators=[MaxValueValidator(10)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        """Serialize field queue item instance"""
        return {
            "id": self.id,
            "field_id": self.field_id,
            "position": self.position,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "created_at": self.created_at,
        }
