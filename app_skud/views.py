from django.views import generic

from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormMixin

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


# class MonitorCheckAccessListView(generic.ListView):
#     model = MonitorCheckAccess
#     context_object_name = "events"
    # form_class = MonitorCheckAccessModelForm
    # success_url = "/app_skud/monitor_list/"  # HARDCODE!!!!!!!

    # def post(self, request, *args, **kwargs):
    #     # внимание говонокод... длжно быть решение лучше по поиску
    #     # избавиться от 2 циклов..
    #     # берется из формы ПК проходной -> находим проходную в БД ->
    #     # получаем список контроллеров данной проходной ->
    #     # перебираем этот список и у каждого контроллера получаем все события ->
    #     # заносим все это в новый список(бред бля) ->
    #     # print(self.get_queryset(), type(self.get_queryset()))
    #     form = self.get_form()
    #     pk_checkpoint = form.data["checkpoint"]
    #     # print(f'id_checkpoint -- >> {pk_checkpoint}')
    #     checkpoint = Checkpoint.objects.get(pk=pk_checkpoint)
    #     # print(f'checkpoint -- >> {checkpoint}')
    #     list_controllers = checkpoint.controller_set.all()
    #     # print(f'list_controllers -- >> {list_controllers}')
    #     list_monitor_checkaccess_select_checkpoint = []
    #     for i in list_controllers:
    #         all_check_access_controller = i.monitorcheckaccess_set.all()
    #         list_monitor_checkaccess_select_checkpoint.append(
    #             all_check_access_controller
    #         )
    #     for jj in list_monitor_checkaccess_select_checkpoint:
    #         el = list_monitor_checkaccess_select_checkpoint[0]
    #         el | jj
    #     # print(f'el___ ---->>> {el} {type(el)}')
    #     if form.is_valid():
    #         return render(
    #             request,
    #             "app_skud/monitorcheckaccess_list.html",
    #             context={"events": el, "form": form},
    #         )
    #         # return self.form_valid(form)
    #     else:
    #         return self.form_invalid(form)
