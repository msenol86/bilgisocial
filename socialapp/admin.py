from socialapp.models import UserMessage, UserLook, UserProfile, UserConversation, UserFeedback, ValidEmail, University, WallPost, UserPhoto, UniversityDepartment
from django.contrib import admin

# class ChoiceInline(admin.TabularInline):
# 	model = Choice
# 	extra = 3

# class PollAdmin(admin.ModelAdmin):
# 	fieldsets = [(None, 			   {'fields' : ['question']}),
# 			  ('Date information', {'fields' : ['pub_date'], 'classes' : ['collapse']})]
# 	inlines = [ChoiceInline]
# 	list_display = ('question', 'pub_date', 'was_published_recently')
# 	list_filter = ['pub_date']
# 	search_fields = ['question']
# 	date_hierarch = 'pub_date'


class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'sender_user', 'receiver_user')


class UserLookAdmin(admin.ModelAdmin):
    list_display = ('looker_user', 'looked_user')


class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('content', 'sent_time', 'read', 'solved')


admin.site.register(UserMessage, UserMessageAdmin)
admin.site.register(UserLook, UserLookAdmin)
admin.site.register(UserProfile)
admin.site.register(UserConversation)
admin.site.register(UserFeedback, UserFeedbackAdmin)
admin.site.register(ValidEmail)
admin.site.register(University)
admin.site.register(WallPost)
admin.site.register(UserPhoto)
admin.site.register(UniversityDepartment)