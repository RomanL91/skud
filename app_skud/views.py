from django.views import generic

from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import (
    Checkpoint,
    Staffs,
    Department,
    Position,
    AccessProfile,
)


class CheckpointListView(generic.ListView):
    model = Checkpoint
    context_object_name = "checkpoints"


class CheckpointCreateView(CreateView):
    model = Checkpoint
    template_name_suffix = "_create_form"
    fields = [
        "name_checkpoint",
        "description_checkpoint",
    ]
    success_url = "/"  # HARDCODE!!!!!!!


class CheckpointDetailView(generic.DetailView):
    model = Checkpoint
    context_object_name = "checkpoint"


class ChecpointUpdateView(UpdateView):
    model = Checkpoint
    template_name_suffix = "_update_form"
    fields = [
        "name_checkpoint",
        "description_checkpoint",
    ]
    success_url = "/"  # HARDCODE!!!!!!!


class CheckpointDeleteView(DeleteView):
    model = Checkpoint
    template_name_suffix = "_delete_form"
    success_url = "/"  # HARDCODE!!!!!!!


# ===============================================================================


class StaffsListView(generic.ListView):
    model = Staffs
    context_object_name = "staffs"


class StaffsCreateView(CreateView):
    model = Staffs
    template_name_suffix = "_create_form"
    fields = [
        "employee_photo",
        "last_name",
        "first_name",
        "patronymic",
        "phone_number",
        "home_address",
        "car_number",
        "car_model",
        "department",
        "position",
        "access_profile",
        "pass_number",
    ]
    success_url = "/"  # HARDCODE!!!!!!!

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        print(f'form --->>> {form.data}')
        return super().post(request, *args, **kwargs)


class StaffsDetailView(generic.DetailView):
    model = Staffs
    context_object_name = "staff"


class StaffsUpdateView(UpdateView):
    model = Staffs
    template_name_suffix = "_update_form"
    fields = [
        "last_name",
        "first_name",
        "patronymic",
        "phone_number",
        "home_address",
        "car_number",
        "car_model",
        "department",
        "position",
        "access_profile",
        "pass_number",
    ]
    success_url = "/"  # HARDCODE!!!!!!!


class StaffDeleteView(DeleteView):
    model = Staffs
    template_name_suffix = "_delete_form"
    success_url = "/"  # HARDCODE!!!!!!!


# ===============================================================================


class DepartmentListView(generic.ListView):
    model = Department
    context_object_name = "departaments"


class DepartamentCreateView(CreateView):
    model = Department
    template_name_suffix = "_create_form"
    fields = [
        "name_departament",
        "abbreviation",
    ]
    success_url = "/"  # HARDCODE!!!!!!!


class DepartamentDetailView(generic.DetailView):
    model = Department
    context_object_name = "departament"


class DepartamentUpdateView(UpdateView):
    model = Department
    template_name_suffix = "_update_form"
    fields = [
        "name_departament",
        "abbreviation",
    ]
    success_url = "/"  # HARDCODE!!!!!!!


class DepartamentDeleteView(DeleteView):
    model = Department
    template_name_suffix = "_delete_form"
    success_url = "/"  # HARDCODE!!!!!!!


# ===============================================================================


class PositionListView(generic.ListView):
    model = Position
    context_object_name = "positions"


class PositionCreateView(CreateView):
    model = Position
    template_name_suffix = "_create_form"
    fields = [
        "name_position",
    ]
    success_url = "/"  # HARDCODE!!!!!!!


class PositionDetailView(generic.DetailView):
    model = Position
    context_object_name = "position"


class PositionUpdateView(UpdateView):
    model = Position
    template_name_suffix = "_update_form"
    fields = [
        "name_position",
    ]
    success_url = "/"  # HARDCODE!!!!!!!


class PositionDeleteView(DeleteView):
    model = Position
    template_name_suffix = "_delete_form"
    success_url = "/"  # HARDCODE!!!!!!!


# ===============================================================================


class AccessProfileListView(generic.ListView):
    model = AccessProfile
    context_object_name = "profiles"


class AccessProfileCreateView(CreateView):
    model = AccessProfile
    template_name_suffix = "_create_form"
    fields = [
        "name_access_profile",
        "description_access_profile",
        "checkpoints",
    ]
    success_url = "/"  # HARDCODE!!!!!!!


class AccessProfileDetailView(generic.DetailView):
    model = AccessProfile
    context_object_name = "profile"


class AccessProfileUpdateView(UpdateView):
    model = AccessProfile
    template_name_suffix = "_update_form"
    fields = [
        "name_access_profile",
        "description_access_profile",
        "checkpoints",
    ]
    success_url = "/"  # HARDCODE!!!!!!!


class AccessProfileDeleteView(DeleteView):
    model = AccessProfile
    template_name_suffix = "_delete_form"
    success_url = "/"  # HARDCODE!!!!!!!


# ===============================================================================
