# coding=utf-8

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from socialapp.models import UserMessage, UserProfile, UserConversation, UserLook, UserFeedback, is_email_unique, get_university_from_email, WallPost, tr_capitalize, UserPhoto, UniversityDepartment
from socialapp.forms import UserForm, SearchForm, FeedbackForm, MyAuthenticationForm, PasswordResetForm, NewPasswordForm, NewPostForm, NewPhotoForm, EditUserProfileForm
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.contrib import messages
import math
import json

import struct

# Create your views here.


# def index(request):
#     if request.user.is_authenticated() and request.user.is_active:
#     # do something for authenticated users.
#         return render_to_response('socialapp/wall.html', {
#             'user': request.user,
#             'logged_in': True,
#             'notifications': get_notifications(request),
#             'arch': 8 * struct.calcsize("P")
#         }, context_instance=RequestContext(request))
#     else:
#         #return HttpResponse("Please log in")
#         return redirect('socialapp.views.login_view')


def login_view(request):
    if request.method == 'POST':
        login_form = MyAuthenticationForm(data=request.POST)
        if login_form.is_valid():
            password = login_form.cleaned_data['password']
            username = login_form.cleaned_data['username']
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                if not user.get_profile().email_activated:
                    messages.error(request,
                                   u'Lütfen e-posta aktivasyonunu gerçekleştirin. Aktivasyon kodunu tekrar göndermek için ' + r'<a href="/send_confirmation_code/' + str(
                                       user.pk) + u'">tıklayın</a>')
                    return render_to_response('socialapp/login.html',
                                              {'form': login_form},
                                              context_instance=RequestContext(request))
                auth.login(request, user)
                return HttpResponseRedirect('/')
    else:
        login_form = MyAuthenticationForm()
    return render_to_response('socialapp/login.html',
                              {'form': login_form},
                              context_instance=RequestContext(request))


def logout_view(request):
    auth.logout(request)
    return redirect('socialapp.views.wall_view')


# def signup_view(request):
#     signup_form = UserForm()
#     if not request.user.is_authenticated:
#         if request.method == 'POST':
#             signup_form = UserForm(request.POST)
#             if signup_form.is_valid():
#                 username = signup_form.cleaned_data['email']
#                 first_name = signup_form.cleaned_data['first_name']
#                 last_name = signup_form.cleaned_data['last_name']
#                 email = signup_form.cleaned_data['email']
#                 password = signup_form.cleaned_data['password']
#                 #university = get_university_from_email(email)
#
#                 if not is_email_unique(email) or university is None:
#                     signup_form = UserForm()
#                 else:
#                     u = User.objects.create_user(username, email, password)
#                     u.first_name = first_name
#                     u.last_name = last_name
#                     u.save()
#                     #send_confirmation_mail()
#                     # up = UserProfile()
#                     # up.user = u
#
#                     # up.birth_date = None
#                     # up.department = ""
#                     # up.university = university
#                     # up.email_activated = True
#                     # up.save()
#                     return redirect('socialapp.views.index')
#             else:
#                 signup_form = UserForm()
#     else:
#         auth.logout(request)
#
#     return render_to_response('socialapp/sign_up.html',
#                                   {'form': signup_form},
#                                   context_instance=RequestContext(request))

def signup_view(request):
    auth.logout(request)
    if request.method == 'POST':
        signup_form = UserForm(request.POST)
        if signup_form.is_valid():
            username = signup_form.cleaned_data['email']
            email = signup_form.cleaned_data['email']
            password = signup_form.cleaned_data['password']
            first_name = signup_form.cleaned_data['first_name']
            last_name = signup_form.cleaned_data['last_name']
            if is_email_unique(email):
                u = User.objects.create_user(username, email, password)
                u.first_name = " ".join(map(lambda x: tr_capitalize(x), first_name.split()))
                u.last_name = tr_capitalize(last_name)
                u.save()
                up = UserProfile()
                up.id = u.id
                up.user = u
                up.university = get_university_from_email(email)
                up.send_confirmation_mail()
                up.save()
                messages.info(request,
                              u"Aktivasyon maili <b>" + u.email + u"</b> adresine gönderildi. Lütfen spam klasörünü de kontrol edin.")
                return redirect('socialapp.views.login_view')
            else:
                #buraya 'bu email zaten var' yazacak şekilde düzenlemeler yap
                messages.error(request, u"Bu email adresi zaten kullanımda")
                signup_form = UserForm()
                return render_to_response('socialapp/sign_up.html',
                                          {'form': signup_form},
                                          context_instance=RequestContext(request))
        else:
            messages.error(request, u"Lütfen formu eksiksiz doldurun")
            signup_form = UserForm()
            return render_to_response('socialapp/sign_up.html',
                                      {'form': signup_form},
                                      context_instance=RequestContext(request))
    else:
        signup_form = UserForm()
        return render_to_response('socialapp/sign_up.html',
                                  {'form': signup_form},
                                  context_instance=RequestContext(request))


@login_required
def messages_view(request, conversation_id, page_number=0):
    current_conversation = UserConversation.objects.get(pk=conversation_id)
    if request.user.is_authenticated() and request.user.is_active and \
            (request.user.pk in UserConversation.get_user_list(current_conversation)):

        if current_conversation.user1.pk == request.user.pk:
            current_conversation.is_new_for_user1 = False
            current_conversation.save()
        elif current_conversation.user2.pk == request.user.pk:
            current_conversation.is_new_for_user2 = False
            current_conversation.save()

        x = UserMessage.objects.filter(conversation=conversation_id).order_by('-sent_time')
        cnt = x.count()
        ll = cnt - 10 * int(page_number) - 10
        #hl = cnt - 10 * int(page_number)
        hl = cnt

        om = False
        if ll > 0:
            om = True

        if ll < 0:
            ll = 0

        return render_to_response('socialapp/messages.html', {
            'message_list': x[ll:hl],
            'old_messages': om,
            'page_number': int(page_number) + 1,
            'user': request.user,
            'interlocutor': current_conversation.get_interlocutor(request.user),
            'logged_in': True,
            'conversation_id': conversation_id,
            'notifications': get_notifications(request)
        }, context_instance=RequestContext(request))
    else:
        return redirect('socialapp.views.wall_view')


def conversations_view(request):
    if request.user.is_authenticated and request.user.is_active:
        return render_to_response('socialapp/conversations.html', {
            'conversation_list': UserConversation.objects.filter(
                Q(user1=request.user) | Q(user2=request.user)).order_by("-update_time"),
            'user': request.user,
            'logged_in': True,
            'notifications': get_notifications(request)
        }, context_instance=RequestContext(request))
    else:
        return redirect('socialapp.views.wall_view')


@login_required
def friends_view(request):
    if request.user.is_authenticated() and request.user.is_active:
        return render_to_response('socialapp/friends.html', {
            'friend_list': UserProfile.objects.get(user=request.user).friends.all(),
            'blocked_list': UserProfile.objects.get(user=request.user).blocked_users.all(),
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'logged_in': True,
            'notifications': get_notifications(request)
        }, context_instance=RequestContext(request))


def send_message(request):
    if request.user.is_authenticated() and request.user.is_active:
        m = UserMessage()
        m.conversation = UserConversation.objects.get(pk=request.POST.get('conversation_id'))
        m.content = request.POST.get('content')
        m.sender_user = User.objects.get(pk=request.user.pk)
        m.receiver_user = User.objects.get(pk=request.POST.get('receiver_user'))
        m.save()
        if m.conversation.user1.pk == request.user.pk:
            m.conversation.is_new_for_user2 = True
        elif m.conversation.user2.pk == request.user.pk:
            m.conversation.is_new_for_user1 = True
        m.conversation.save()
        return redirect('socialapp.views.messages_view', request.POST.get('conversation_id'))


@login_required
def my_profile_view(request):
    if request.user.is_authenticated() and request.user.is_active:
        up = UserProfile.objects.get(user=request.user)
        return render_to_response('socialapp/profile.html', {
            'user_profile': up,
            'logged_in': True,
            'notifications': get_notifications(request),
            'other_user': False,
        }, context_instance=RequestContext(request))


@login_required
def profile_view(request, user_id):
    if request.user.is_authenticated() and request.user.is_active:
        if long(request.user.pk) != long(user_id):
            wink(request.user, user_id)
        up = UserProfile.objects.get(user=User.objects.get(pk=user_id))
        return render_to_response('socialapp/profile.html', {
            'user_profile': up,
            'logged_in': True,
            'notifications': get_notifications(request),
            'other_user': int(user_id) != int(request.user.pk),
            'active_user': User.objects.get(pk=request.user.pk),
        }, context_instance=RequestContext(request))


@login_required
def looks_view(request):
    if request.user.is_authenticated() and request.user.is_active:
        look_list = UserLook.objects.filter(looked_user=request.user)

        look_list_for_template = []
        for look_object in look_list:
            look_list_for_template += [{'looker_user': look_object.looker_user, 'highlight': not look_object.is_seen}]

        for look_object in look_list:
            look_object.is_seen = True
            look_object.save()

        return render_to_response('socialapp/looks.html', {
            'look_list': look_list_for_template,
            'logged_in': True,
            'notifications': get_notifications(request),
        }, context_instance=RequestContext(request))


def get_notifications(request):
    if request.user.is_authenticated() and request.user.is_active:
        look_count = len(UserLook.objects.filter(looked_user=request.user, is_seen=False))

        message_count = UserConversation.get_unread_conversation_count(request.user)
        return {'look_count': look_count,
                'message_count': message_count}


def start_conversation(request, other_user_id):
    if request.user.is_authenticated() and request.user.is_active:
        q1 = UserConversation.objects.filter(user1=request.user, user2=User.objects.get(pk=other_user_id))
        q2 = UserConversation.objects.filter(user2=request.user, user1=User.objects.get(pk=other_user_id))
        conversation_id = 0
        if not q1 and not q2:
            uc = UserConversation()
            uc.user1 = request.user
            uc.user2 = User.objects.get(pk=other_user_id)
            uc.save()
            conversation_id = uc.pk
        elif not q1 and len(q2) == 1:
            conversation_id = q2[0].pk
        elif not q2 and len(q1) == 1:
            conversation_id = q1[0].pk
        return redirect('socialapp.views.messages_view', conversation_id)


def add_friend(request, friend_id):
    if request.user.is_authenticated() and request.user.is_active:
        u = User.objects.get(pk=request.user.pk)
        p = u.get_profile()
        p.friends.add(User.objects.get(pk=friend_id).get_profile())
        p.save()
        return redirect('socialapp.views.wall_view')


def remove_friend(request, friend_id):
    if request.user.is_authenticated() and request.user.is_active:
        u = User.objects.get(pk=request.user.pk)
        p = u.get_profile()
        p.friends.remove(User.objects.get(pk=friend_id).get_profile())
        p.save()
        return redirect('socialapp.views.wall_view')


def wink(looker_user, other_user_id):
    u = UserLook()
    u.looker_user = looker_user
    u.looked_user = User.objects.get(pk=other_user_id)
    u.save()


# @login_required
# def search_view(request):
#     if request.method == 'GET':
#         search_form = SearchForm(request.GET)
#         if search_form.is_valid():
#             first_name = search_form.cleaned_data['first_name']
#             last_name = search_form.cleaned_data['last_name']
#             users = User.objects.filter(first_name=first_name, last_name=last_name)
#             user_profiles = []
#             for u in users:
#                 user_profiles = user_profiles + [UserProfile.objects.get(user=u)]
#             return render_to_response('socialapp/result.html',
#                                       {'users': user_profiles, 'logged_in': True, 'user': request.user,
#                                        'notifications': get_notifications(request)},
#                                       context_instance=RequestContext(request))
#         else:
#             search_form = SearchForm()
#             return render_to_response('socialapp/search.html',
#                                       {'form': search_form,
#                                        'logged_in': True,
#                                        'user': request.user,
#                                        'notifications': get_notifications(request)},
#                                       context_instance=RequestContext(request))

@login_required
def search_view(request):
    search_text = request.GET["search_text"]
    trimmed_search_text = search_text.strip().split(" ")

    if len(trimmed_search_text) > 1:
        first_names = " ".join(trimmed_search_text[:-1])
        last_name = trimmed_search_text[-1]
        users = User.objects.filter(Q(first_name__istartswith=first_names) | Q(last_name__startswith=last_name))

    else:
        users = User.objects.filter(first_name__istartswith=trimmed_search_text[0])

    found_users = []
    for u in users:
        user_profile = UserProfile.objects.get(user=u)
        found_users += [{'picture': str(user_profile.picture), 'full_name': u.get_full_name(), 'id': str(u.id)}]

    return HttpResponse(json.dumps(found_users), mimetype='application/json')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def feedback_view(request):
    if request.method == 'POST':
        feedback_form = FeedbackForm(request.POST)
        if feedback_form.is_valid():
            f = UserFeedback()
            if request.user is not None and request.user.is_active:
                f.user = request.user
            f.content = feedback_form.cleaned_data['content']
            f.ip = get_client_ip(request)
            f.save()
            return HttpResponseRedirect(request.POST.get('next', ''))
        else:
            feedback_form = FeedbackForm()
            messages.error(request,
                           u"Forma eksik bilgi girdiniz")
            return render_to_response('socialapp/feedback.html',
                                      {'form': feedback_form,
                                       'logged_in': request.user.is_authenticated,
                                       'notifications': get_notifications(request),
                                       'user': request.user,
                                       'next': request.POST.get('next', '')},
                                      context_instance=RequestContext(request))
    else:
        next = request.GET['next']
        feedback_form = FeedbackForm()
        return render_to_response('socialapp/feedback.html',
                                  {'form': feedback_form,
                                   'logged_in': request.user.is_authenticated,
                                   'notifications': get_notifications(request),
                                   'user': request.user,
                                   'next': next},
                                  context_instance=RequestContext(request))


@login_required()
def wall_view(request, page_number=1):
    posts = WallPost.objects.all().order_by("-update_time")
    page_number = int(page_number) - 1 # just for indexing

    #x = UserMessage.objects.filter(conversation=conversation_id).order_by('-sent_time')
    cnt = posts.count()
    page_limit = 20

    #ll = cnt - page_limit * int(page_number) - page_limit
    #hl = cnt - page_limit * int(page_number)

    ll = page_number * page_limit
    hl = (page_number * page_limit) + page_limit

    if ll < 0:
        ll = 0

    if hl < ll:
        hl = ll

    current_posts = posts[ll:hl]

    return render_to_response('socialapp/wall.html',
                              {'logged_in': request.user.is_authenticated,
                               'notifications': get_notifications(request),
                               'user': request.user,
                               'next': next,
                               'posts': current_posts,
                               'number_of_pages': range(1, int(math.ceil(cnt / float(page_limit) + 1))),
                               'current_page': page_number + 1},
                              context_instance=RequestContext(request))


@login_required()
def post_view(request, post_id):
    post = WallPost.objects.get(pk=post_id)
    return render_to_response('socialapp/post.html',
                              {'logged_in': request.user.is_authenticated,
                               'notifications': get_notifications(request),
                               'user_profile': UserProfile.objects.get(user=request.user),
                               'is_owner': post.user.pk == request.user.pk,
                               'next': next,
                               'post': post},
                              context_instance=RequestContext(request))


@login_required()
def block_user(request, user_profile_id):
    u = User.objects.get(pk=request.user.pk)
    p = u.get_profile()
    p.blocked_users.add(UserProfile.objects.get(pk=user_profile_id))
    p.save()
    return redirect('socialapp.views.wall_view')


@login_required()
def unblock_user(request, user_profile_id):
    u = User.objects.get(pk=request.user.pk)
    p = u.get_profile()
    p.blocked_users.remove(UserProfile.objects.get(pk=user_profile_id))
    p.save()
    return redirect('socialapp.views.wall_view')


def send_confirm_view(request, user_id):
    u = User.objects.get(pk=user_id)
    p = u.get_profile()
    p.send_confirmation_mail_and_save()
    messages.info(request,
                  u"Aktivasyon maili <b>" + u.email + u"</b> adresine gönderildi. Lütfen spam klasörünü de kontrol edin.")
    return redirect('socialapp.views.login_view')


def confirm_user(request, user_id, confirm_code):
    u = User.objects.get(pk=user_id)
    p = u.get_profile()
    if p.confirmation_code == confirm_code:
        p.email_activated = True
        p.save()
        messages.info(request, u"E-mail aktivasyonunuz başarılı bir şekilde gerçekleştirildi. Giriş yapın")
        return redirect('socialapp.views.login_view')
    else:
        messages.error(request, u"E-mail aktivasyonunuz başarısız oldu")
        return redirect('socialapp.views.login_view')


def set_new_password(request, user_id):
    if user_id == "0":
        user_id = request.user.pk

    print(user_id)

    if request.method == 'POST':
        new_password_form = NewPasswordForm(request.POST)
        if new_password_form.is_valid():
            if new_password_form.cleaned_data['new_password'] == new_password_form.cleaned_data['new_password_confirm']:
                u = User.objects.get(pk=user_id)
                print(new_password_form.cleaned_data['new_password'])
                u.set_password(new_password_form.cleaned_data['new_password'])
                u.save()

                messages.success(request, u"Yeni parolanız kaydedildi. Giriş yapın.")
                return redirect('socialapp.views.login_view')
            else:
                messages.error(request, u"Lütfen parolanızı doğru girin.")
                return redirect('socialapp.views.set_new_password', user_id)
        else:
            messages.error(request, u"Lütfen parolanızı doğru girin.")
            return redirect('socialapp.views.set_new_password', user_id)

    else:
        return render_to_response('socialapp/new_password.html',
                                  {'form': NewPasswordForm(),
                                   'user_id': user_id},
                                  context_instance=RequestContext(request))


def reset_password(request, user_id=0, password_reset_code=0):
    auth.logout(request)

    if user_id != 0 and password_reset_code != 0:
        u = User.objects.get(pk=user_id)
        p = UserProfile.objects.get(user=u, password_reset_code=password_reset_code)
        if p is not None:
            return redirect('socialapp.views.set_new_password', user_id)

    elif request.method == 'POST':
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            u = User.objects.get(email=password_reset_form.cleaned_data['email'])
            print u.email
            p = u.get_profile()
            p.send_password_reset_mail_and_save()
            messages.success(request,
                             u"Parola sıfırlama maili <b>" + u.email + u"</b> adresine gönderildi. Lütfen spam klasörünü de kontrol edin.")
            return redirect('socialapp.views.reset_password')
        else:
            messages.error(request, u"Bir hata oluştu.")
            return redirect('socialapp.views.reset_password')

    else:
        password_reset_form = PasswordResetForm(request.POST)
        return render_to_response('socialapp/password_reset.html',
                                  {'form': password_reset_form},
                                  context_instance=RequestContext(request))


@login_required()
def submit_wall_post_view(request, wall_post_id=0):
    if request.method == 'POST':
        wall_post_form = NewPostForm(request.POST)
        if wall_post_form.is_valid():
            if wall_post_id != 0 and WallPost.objects.filter(pk=int(wall_post_id), user=request.user):
                w = WallPost.objects.get(pk=int(wall_post_id))
            else:
                w = WallPost()
            w.title = wall_post_form.cleaned_data['title']
            w.content = wall_post_form.cleaned_data['content']
            w.user = request.user
            w.save()
            return redirect('/posts/' + str(w.pk))
        else:
            messages.error(request, u"Forma eksik bilgi girdiniz")
            return render_to_response('socialapp/new_post.html',
                                      {'form': wall_post_form,
                                       'logged_in': request.user.is_authenticated},
                                      context_instance=RequestContext(request))
    elif wall_post_id == 0:
        return render_to_response('socialapp/new_post.html',
                                  {'form': NewPostForm(),
                                   'logged_in': request.user.is_authenticated},
                                  context_instance=RequestContext(request))
    else:
        if WallPost.objects.filter(pk=int(wall_post_id), user=request.user).count() != 0:
            wp = WallPost.objects.get(pk=int(wall_post_id))
            form = NewPostForm(
                initial={'title': wp.title, 'content': wp.content})
            return render_to_response('socialapp/new_post.html',
                                      {'form': form,
                                       'wall_post': wp,
                                       'logged_in': request.user.is_authenticated},
                                      context_instance=RequestContext(request))
        else:
            messages.error(request, u"Bu içerik erişilemez")
            return redirect('/')


@login_required
def photos_view(request, user_id, photo_number=1):
    photo_number = int(photo_number)
    photos = UserPhoto.objects.filter(user=User.objects.get(pk=user_id)).order_by("-create_time")
    cnt = photos.count()
    if cnt <= 0:
        return render_to_response('socialapp/photos.html',
                                  {'logged_in': request.user.is_authenticated, 'no_photo': True,
                                   'notifications': get_notifications(request)},
                                  context_instance=RequestContext(request))
    else:
        photo = photos[photo_number - 1]
        return render_to_response('socialapp/photos.html',
                                  {'photo': photo,
                                   'logged_in': request.user.is_authenticated,
                                   'notifications': get_notifications(request),
                                   'previous_photo': photo_number - 1,
                                   'next_photo': photo_number + 1,
                                   'photo_count': cnt,
                                   'current_photo': photo_number,
                                   'user_id': user_id,
                                   'is_owner': request.user.pk == int(user_id)},
                                  context_instance=RequestContext(request))


@login_required
def remove_photo(request, photo_id):
    photo_id = int(photo_id)
    UserPhoto.objects.filter(user=request.user, pk=photo_id).delete()
    if UserPhoto.objects.filter(user=request.user, pk=photo_id).count() == 0:
        messages.success(request, u"Fotoğrafınız başarıyla silindi")
        return redirect('socialapp.views.photos_view', request.user.pk)
    else:
        messages.error(request, u"Bir hata oluştu")
        return redirect('socialapp.views.photos_view', request.user.pk)


@login_required
def add_photo_view(request):
    if request.method == 'POST':
        form = NewPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            p = UserPhoto()
            p.user = request.user
            p.title = form.cleaned_data['title']
            p.file_name = request.FILES['file_name']
            p.save()
            messages.success(request, u"Fotoğrafınız başarıyla eklendi")
            return redirect("socialapp.views.add_photo_view")
        else:
            print(form._errors)
            messages.error(request, u"Bir hata oluştu")
            return render_to_response('socialapp/add_photo.html',
                                      {'logged_in': request.user.is_authenticated,
                                       'notifications': get_notifications(request),
                                       'user_id': request.user.pk,
                                       'form': NewPhotoForm(request.POST)},
                                      context_instance=RequestContext(request))

    else:
        form = NewPhotoForm()
        return render_to_response('socialapp/add_photo.html',
                                  {'logged_in': request.user.is_authenticated,
                                   'notifications': get_notifications(request),
                                   'user_id': request.user.pk,
                                   'form': form},
                                  context_instance=RequestContext(request))


@login_required
def edit_user_profile_view(request):
    if request.method == 'POST':
        form = EditUserProfileForm(request.POST)
        if form.is_valid():
            up = request.user.get_profile()
            up.birth_date = form.cleaned_data['birth_date']

            up.department = form.cleaned_data['department']
            up.about = form.cleaned_data['about']
            up.save()
            messages.success(request, u"Profiliniz başarıyla güncellendi")
            return render_to_response('socialapp/edit_user_profile.html',
                                      {'logged_in': request.user.is_authenticated,
                                       'notifications': get_notifications(request),
                                       'user_profile_id': request.user.get_profile().id,
                                       'form': form}, context_instance=RequestContext(request))
        else:
            messages.error(request, u"Formu yanlış doldurdunuz. Lütfen tekrar deneyin")
            return render_to_response('socialapp/edit_user_profile.html',
                                      {'logged_in': request.user.is_authenticated,
                                       'notifications': get_notifications(request),
                                       'user_profile_id': request.user.get_profile().id,
                                       'form': form}, context_instance=RequestContext(request))
    else:
        up = request.user.get_profile()
        form = EditUserProfileForm(
            initial={'birth_date': up.birth_date, 'department': up.department, 'about': up.about})
        return render_to_response('socialapp/edit_user_profile.html',
                                  {'logged_in': request.user.is_authenticated,
                                   'notifications': get_notifications(request),
                                   'user_profile_id': request.user.get_profile().id,
                                   'form': form}, context_instance=RequestContext(request))


@login_required
def make_profile_picture(request, photo_id):
    up = request.user.get_profile()
    up.picture = UserPhoto.objects.get(pk=photo_id, user=request.user).file_name
    up.save()
    return redirect("socialapp.views.my_profile_view")

