from django.conf.urls import patterns, include, url
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'social.views.home', name='home'),
    # url(r'^social/', include('social.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'socialapp.views.wall_view'),
    url(r'^(?P<page_number>\d+)$', 'socialapp.views.wall_view'),
    url(r'^signup/', 'socialapp.views.signup_view'),
    url(r'^login/$', 'socialapp.views.login_view'),
    url(r'^logout/$', 'socialapp.views.logout_view'),
    url(r'^messages/$', 'socialapp.views.conversations_view'),
    url(r'^messages/send/$', 'socialapp.views.send_message'),
    url(r'^messages/(?P<conversation_id>\d+)/(?P<page_number>\d+)$', 'socialapp.views.messages_view'),
    url(r'^messages/(?P<conversation_id>\d+)$', 'socialapp.views.messages_view'),
    url(r'^friends/$', 'socialapp.views.friends_view'),
    url(r'^profile/$', 'socialapp.views.my_profile_view'),
    url(r'^profile/(?P<user_id>\d+)$', 'socialapp.views.profile_view'),
    url(r'^looks/$', 'socialapp.views.looks_view'),
    url(r'^start_conversation/(?P<other_user_id>\d+)$', 'socialapp.views.start_conversation'),
    url(r'^add_friend/(?P<friend_id>\d+)$', 'socialapp.views.add_friend'),
    url(r'^remove_friend/(?P<friend_id>\d+)$', 'socialapp.views.remove_friend'),
    url(r'^block_user/(?P<user_profile_id>\d+)$', 'socialapp.views.block_user'),
    url(r'^unblock_user/(?P<user_profile_id>\d+)$', 'socialapp.views.unblock_user'),
    url(r'^search/$', 'socialapp.views.search_view'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^feedback/', 'socialapp.views.feedback_view'),
    url(r'^wall/', 'socialapp.views.wall_view'),
    url(r'^posts/(?P<post_id>\d+)$', 'socialapp.views.post_view'),
    url(r'^send_confirmation_code/(?P<user_id>\d+)$', 'socialapp.views.send_confirm_view'),
    url(r'^confirm_user/(?P<user_id>\d+)/(?P<confirm_code>\w+)$', 'socialapp.views.confirm_user'),
    url(r'^password_reset/$', 'socialapp.views.reset_password'),
    url(r'^password_reset/(?P<user_id>\d+)/(?P<password_reset_code>\w+)$', 'socialapp.views.reset_password'),
    url(r'^new_password/(?P<user_id>\d+)$', 'socialapp.views.set_new_password'),
    url(r'^manage_post/$', 'socialapp.views.submit_wall_post_view'),
    url(r'^photos/(?P<user_id>\d+)$', 'socialapp.views.photos_view'),
    url(r'^photos/(?P<user_id>\d+)/(?P<photo_number>\d+)$', 'socialapp.views.photos_view'),
    url(r'^add_photo$', 'socialapp.views.add_photo_view'),
    url(r'^remove_photo/(?P<photo_id>\d+)$', 'socialapp.views.remove_photo'),
    url(r'^edit_user_profile/$', 'socialapp.views.edit_user_profile_view'),
    url(r'^set_profile_picture/(?P<photo_id>\d+)$', 'socialapp.views.make_profile_picture'),
    url(r'^manage_post/(?P<wall_post_id>\d+)$', 'socialapp.views.submit_wall_post_view'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                 {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                 {'document_root': settings.STATIC_ROOT}),
)
