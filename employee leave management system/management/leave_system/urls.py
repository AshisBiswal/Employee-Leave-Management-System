from django.contrib import admin

from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.register,name='register'),
    path('login/',views.login_f,name='login'),
    path('employee/',views.employee,name='employee'),
    path('apply_leave/',views.leave_request,name='apply_leave'),
    path('applied/',views.applied,name='applied'),
    path('manager/',views.manager,name='manager'),
    path('notifications/',views.notification,name='notifications'),
    path('requests/',views.requests,name='requests'),
    path('approve/<int:request_id>/', views.approve_leave, name='approve_leave'),
    path('reject/<int:request_id>/', views.reject_leave, name='reject_leave'),
    path('leave_events/', views.leave_events, name='leave_events'),
    path('calendar/', views.calendar, name='calendar_view'),
    path('comment/<int:leave_id>/', views.add_comment, name='comment'),
    path('leave_comment/<int:leave_id>/', views.leave_comment, name='leave_comment'),
    path('delete_notification/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('markread_notification/<int:notification_id>/', views.markread_notification, name='markread_notification'),
    path('manager_comment/<int:leave_id>/', views.manager_comment, name='manager_comment'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment')

]
