from django.contrib import messages
from django.contrib.auth import logout, login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import FormView, UpdateView

from PokerApp.forms import CustomUserCreationForm, CustomUserChangeForm
from PokerApp.models import CustomUser, Bot


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


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("/")


def profile(request, username):
    user = CustomUser.objects.filter(username=username).all()
    return render(request, 'profile.html', {'user_object': user})


class UpdateProfile(UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'profile_editing.html'
    success_url = '/'


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('index')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


def game(request, user):
    user_active = CustomUser.objects.filter(username=user).all()
    bots = Bot.objects.filter().all()
    return render(request, 'game.html', locals())
