from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    roles = [('employee','Employee'),('manager','Manager')]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=roles)
    email = models.EmailField()

    def __str__(self) -> str:
        return f"{self.user.username}"
    

class Leave(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    TYPE_CHOICES = [
        ("Vacation", "Vacation"),
        ("Sick", "Sick")
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=500)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='pending')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    manager = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='assigned_leaves', null=True, blank=True)

    def __str__(self):
        return f"Leave for {self.profile.user.username} from {self.start_date} to {self.end_date}"

    @property
    def available_managers(self):
        return Profile.objects.filter(role='manager')

class Request(models.Model):
    leave = models.ForeignKey(Leave, on_delete=models.CASCADE, related_name='request')
    manager = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='leave_requests')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Leave Request for {self.leave.profile.user.username} submitted to {self.manager.user.username}"

class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    leave = models.ForeignKey(Leave, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=[('unread', 'Unread'), ('read', 'Read')], default='unread')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username} regarding leave {self.leave.id}"
    

class Comment(models.Model):
    leave = models.ForeignKey(Leave, on_delete=models.CASCADE, related_name='comments', default=None, null=True)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.commenter.username} on leave request {self.leave.id}"