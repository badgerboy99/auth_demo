# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from accounts.forms import UserRegistrationForm, UserLoginForm
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
import datetime
import stripe

stripe.api_key = settings.STRIPE_SECRET


def register(request):
    if request.method =='POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                customer = stripe.Charge.create(
                    amount =999,
                    currency="GBP",
                    description=form.cleaned_data['email'],
                    card=form.cleaned_data['stripe_id'],
                )
                if customer.paid:
                    form.save()
                    user= auth.authenticate(email=request.POST.get('email'),
                                            password=request.POST.get('password1'))

                    if user:
                        auth.login(request, user)
                        messages.success(request, "You have successfully registered")
                        return redirect(reverse('profile'))
                    else:
                        messages.error(request, "unable to log you in at this time!")
                else:
                    messages.error(request, "We were unable to take a payment with that card!")
            except stripe.error.CardError, e:
                messages.error(request, "Your card was declined!")
    else:
        today = datetime.date.today()
        form = UserRegistrationForm()

    args = {'form': form, 'publishable': settings.STRIPE_PUBLISHABLE }
    args.update(csrf(request))

    return render(request, 'register.html', args)
