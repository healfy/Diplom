from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm

from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import FormView

from PokerApp.forms import CustomUserCreationForm


def main(request):
    return render(request, 'index.html')


class RegisterFormView(FormView):
    form_class = CustomUserCreationForm
    success_url = "/login/"
    template_name = "registration.html"

    def form_valid(self, form):
        form.save()
        return super(RegisterFormView, self).form_valid(form)


class LoginFormView(FormView):
    form_class = AuthenticationForm
    template_name = "login.html"
    success_url = "/"

    def form_valid(self, form):
        self.user = form.get_user()

        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)

    def form_invalid(self, form):
        print()


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("/")
