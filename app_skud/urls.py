from django.urls import path

from .views import (
    CheckpointListView, CheckpointCreateView,
    CheckpointDetailView, ChecpointUpdateView,
    CheckpointDeleteView,
    # 
    StaffsListView, StaffsCreateView, StaffsDetailView,
    StaffsUpdateView, StaffDeleteView,
    # 
    DepartmentListView, DepartamentCreateView,
    DepartamentDetailView, DepartamentUpdateView,
    DepartamentDeleteView,
    # 
    PositionListView, PositionCreateView, PositionDetailView,
    PositionUpdateView, PositionDeleteView,
    # 
    AccessProfileListView, AccessProfileCreateView, AccessProfileDetailView,
    AccessProfileUpdateView, AccessProfileDeleteView,
    # 
)


urlpatterns = [
    # 
    path('checkpoints_list/', CheckpointListView.as_view(), name='checkpoints_list'),
    path('checkpoints_new/', CheckpointCreateView.as_view(), name='checkpoints_new'),
    path('checkpoint/<int:pk>/', CheckpointDetailView.as_view(), name='checkpoint'),
    path('checkpoint/<int:pk>/edit/', ChecpointUpdateView.as_view(), name='checkpoint_edit'),
    path('checkpoint/<int:pk>/delete/', CheckpointDeleteView.as_view(), name='checkpoint_delete'),
    # 
    path('staffs_list/', StaffsListView.as_view(), name='staffs_list'),
    path('staff_new/', StaffsCreateView.as_view(), name='staff_new'),
    path('staff/<int:pk>/', StaffsDetailView.as_view(), name='staff'),
    path('staff/<int:pk>/edit/', StaffsUpdateView.as_view(), name='staff_edit'),
    path('staff/<int:pk>/delete/', StaffDeleteView.as_view(), name='staff_delete'),
    # 
    path('departaments_list/', DepartmentListView.as_view(), name='departaments_list'),
    path('departament_new/', DepartamentCreateView.as_view(), name='departament_new'),
    path('departament/<int:pk>/', DepartamentDetailView.as_view(), name='departament'),
    path('departament/<int:pk>/edit/', DepartamentUpdateView.as_view(), name='departament_edit'),
    path('departament/<int:pk>/delete/', DepartamentDeleteView.as_view(), name='departament_delete'),
    # 
    path('positions_list/', PositionListView.as_view(), name='positions_list'),
    path('position_new/', PositionCreateView.as_view(), name='position_new'),
    path('position/<int:pk>/', PositionDetailView.as_view(), name='position'),
    path('position/<int:pk>/edit/', PositionUpdateView.as_view(), name='position_edit'),
    path('position/<int:pk>/delete/', PositionDeleteView.as_view(), name='position_delete'),
    # 
    path('profiles_list/', AccessProfileListView.as_view(), name='profiles_list'),
    path('profile_new/', AccessProfileCreateView.as_view(), name='profile_new'),
    path('profile/<int:pk>/', AccessProfileDetailView.as_view(), name='profile'),
    path('profile/<int:pk>/edit/', AccessProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/<int:pk>/delete/', AccessProfileDeleteView.as_view(), name='profile_delete'),
    # 
]