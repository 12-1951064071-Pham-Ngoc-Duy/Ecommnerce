from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from carts.models import Cart, CartItem
from orders.models import Order, OrderProduct
from .form import RegistrationForm, UserForm, UserProfileForm,UserProfile
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

#Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.views import _cart_id
import requests
from django.contrib.auth.hashers import make_password

# Create your views here.
def is_digit(s):
    return s.isdigit()
def register(request):
    if request.method == 'POST':
        registration_form = RegistrationForm(request.POST, request.FILES)
        profile_picture = UserProfileForm(request.POST, request.FILES)
        if registration_form.is_valid():
            phone_number = registration_form.cleaned_data['phone_number']
            password = registration_form.cleaned_data['password']
            hashed_password = make_password(password)
            if Account.objects.filter(phone_number=phone_number).exists():
                messages.error(request, 'Your phone number already exists')
                return redirect('register')
            elif len(password) < 8:
                messages.error(request, 'Password must be at least 8 characters long')
                return redirect('register')
            elif not all(is_digit(c) for c in phone_number):
                messages.error(request, 'Phone number must contain only digits')
                return redirect('register')
            else:
                first_name = registration_form.cleaned_data['first_name']
                last_name = registration_form.cleaned_data['last_name']
                phone_number = registration_form.cleaned_data['phone_number']
                email = registration_form.cleaned_data['email']
                password = registration_form.cleaned_data['password']
                username = email.split("@")[0]
                user = Account.objects.create(first_name=first_name, last_name=last_name,email=email,username=username,password=hashed_password)
                user.phone_number = phone_number
                user.save()

                profile = profile_picture.save(commit=False)
                profile.user = user
                profile.save()

                current_site = get_current_site(request)
                mail_subject = 'Please activate your account'
                message = render_to_string('accounts/account_verification_email.html', {
                    'user': user,
                    'domain': current_site, 
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                to_email = email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.send()

            # messages.success(request, 'Thanks you for registering with us. We have sent you a verification email to your email address')
                return redirect('/accounts/login/?command=verification&email='+email)
        else:
            email = request.POST.get('email')
            password = request.POST.get('password')
            re_password = request.POST.get('re_password')
            if Account.objects.filter(email=email).exists():
                messages.error(request, 'Your email already exists')
                return redirect('register')
            if  password != re_password:
                messages.error(request, 'Your password not match')
                return redirect('register')
            
    else:
        registration_form = RegistrationForm()
        profile_form = UserProfileForm()
    context = {
        'registration_form':registration_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = auth.authenticate(email=email,password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart = cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    cart_item = CartItem.objects.filter(user = user)
                    ex_var_list=[]
                    id = []
                    for item in cart_item:
                       existing_variation = item.variations.all()
                       ex_var_list.append(list(existing_variation))
                       id.append(item.id)
                    
                    # product_variation = [1, 2, 3, 4, 6]
                    # ex_var_list = [4, 6, 3, 5]
                    
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                               item.user = user
                               item.save()
                     
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'Your are bow logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
                
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Coongratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
    
def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')
    
@login_required(login_url = 'login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    order_count = orders.count()

    userprofile = UserProfile.objects.get(user_id=request.user.id)

    context = {
        'order_count': order_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            
            #reset Pasword Email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site, 
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')

        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        re_password = request.POST['re_password']

        if password == re_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')
    
@login_required(login_url = 'login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url = 'login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            phone_number = user_form.cleaned_data['phone_number']
            if Account.objects.filter(phone_number=phone_number).exists():
                messages.error(request, 'Your phone number already exists')
                return redirect('edit_profile')
            elif not all(is_digit(c) for c in phone_number):
                messages.error(request, 'Phone number must contain only digits')
                return redirect('edit_profile')
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form':user_form,
        'profile_form':profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url = 'login')
def changePassword(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        re_password = request.POST['re_password']
        
        user = Account.objects.get(username__exact=request.user.username)

        if new_password == re_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()

                messages.success(request, 'Password updated successfully. Please logged again')
                return redirect('changePassword')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('changePassword')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('changePassword')
    return render(request, 'accounts/changePassword.html')

@login_required(login_url = 'login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)