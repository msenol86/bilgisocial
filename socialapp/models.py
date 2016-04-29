# coding=utf-8


from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
import re
import hashlib
from datetime import datetime
from django.core.mail import send_mail

# Create your models here.


def tr_capitalize(text):
    for i in range(0, len(text)):
        if text[i] == u"i":
            return u"İ" + text[i+1:]
        elif text[i] == u"ı":
            return u"I" + text[i+1:]
        else:
            return text.capitalize()


class UserConversation(models.Model):
    user1 = models.ForeignKey(User, related_name='user1')
    user2 = models.ForeignKey(User, related_name='user2')
    update_time = models.DateTimeField(auto_now=True)
    is_new_for_user1 = models.BooleanField(default=False)
    is_new_for_user2 = models.BooleanField(default=False)

    def get_user_list(self):
        return [self.user1.pk, self.user2.pk]

    def is_user_in_conversation(self, user):
        if user.pk in self.get_user_list():
            return True
        else:
            return False

    def get_interlocutor(self, user):
        if self.is_user_in_conversation(user):
            x = self.get_user_list()
            x.remove(user.pk)
            return x.pop()
        else:
            raise LookupError

    @staticmethod
    def get_conversations_of_user(user):
        return UserConversation.objects.filter(Q(user1=user) | Q(user2=user))

    @staticmethod
    def get_unread_conversation_count(user):
        count = 0
        for conversation in UserConversation.get_conversations_of_user(user):
            if conversation.user1.pk == user.pk and conversation.is_new_for_user1:
                count += 1
            elif conversation.user2.pk == user.pk and conversation.is_new_for_user2:
                count += 1
        return count

    def __unicode__(self):
        return self.user1.get_full_name() + " - " + self.user2.get_full_name()


class UserMessage(models.Model):
    content = models.TextField()
    sender_user = models.ForeignKey(User, related_name='message_sender')
    receiver_user = models.ForeignKey(User, related_name='message_receiver')
    sent_time = models.DateTimeField(auto_now_add=True)
    conversation = models.ForeignKey(UserConversation)

    def __unicode__(self):
        return self.content


class UserLook(models.Model):
    looker_user = models.ForeignKey(User, related_name='looker')
    looked_user = models.ForeignKey(User, related_name='looked')
    is_seen = models.BooleanField(default=False)
    wink_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.looker_user)


class University(models.Model):
    title = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="logos/")

    def __unicode__(self):
        return self.title


class UniversityDepartment(models.Model):
    title = models.CharField(max_length=254)
    university = models.ManyToManyField(University, related_name="university_of_department")

    def __unicode__(self):
        return self.title


class ValidEmail(models.Model):
    email_extension = models.CharField(max_length=50)
    universities = models.ForeignKey(University, blank=True, null=True)

    def __unicode__(self):
        return self.email_extension


class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True)

    picture = models.ImageField(upload_to='user_pictures/', blank=True, default='user_pictures/default-user.png')
    birth_date = models.DateField(blank=True, null=True)
    university = models.ForeignKey(University, blank=True, null=True)
    department = models.ForeignKey(UniversityDepartment, blank=True, null=True)
    friends = models.ManyToManyField("self", symmetrical=False, blank=True, null=True, related_name="user_friends")
    email_activated = models.BooleanField(default=True)
    about = models.TextField(blank=True, null=True)
    blocked_users = models.ManyToManyField("self", symmetrical=False, blank=True, null=True, related_name="user_blocked_users")
    confirmation_code = models.CharField(max_length=50)
    password_reset_code = models.CharField(max_length=50, blank=True, null=True)

    def send_password_reset_mail_and_save(self):
        m = hashlib.md5()
        m.update(self.user.email + str(datetime.now()) + self.user.password)
        self.password_reset_code = m.hexdigest()
        send_mail(u'Parola Sıfırlama', 'http://www.bilgisocial.com/password_reset/' + str(self.user.pk) + "/" + self.password_reset_code, 'password-reset@bilgisocial.com', [self.user.email])
        self.save()

    def send_confirmation_mail(self):
        m = hashlib.md5()
        m.update(self.user.email + str(datetime.now()))
        self.confirmation_code = m.hexdigest()
        send_mail(u'Üyelik Aktivasyon', 'http://www.bilgisocial.com/confirm_user/' + str(self.user.pk) + "/"+ self.confirmation_code, 'no-reply@bilgisocial.com', [self.user.email])
        self.email_activated = False

    def send_confirmation_mail_and_save(self):
        self.send_confirmation_mail()
        self.save()

    def __unicode__(self):
        return self.user.first_name + " " + self.user.last_name


class UserFeedback(models.Model):
    content = models.TextField()
    user = models.ForeignKey(User, null=True, blank=True, default=None)
    sent_time = models.DateTimeField(auto_now_add=True)
    ip = models.IPAddressField()
    read = models.BooleanField(default=False)
    solved = models.BooleanField(default=False)

    def __unicode__(self):
        if self.user is None:
            return self.content[:10] + "... " + unicode(self.ip)
        else:
            return self.content[:10] + "... " + unicode(self.user.get_full_name())


class WallPost(models.Model):
    title = models.CharField(max_length=150)
    content = models.TextField()
    user = models.ForeignKey(User)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title + " - " + self.user.get_full_name()


def is_email_unique(email):
    if not User.objects.filter(email=email):
        if not User.objects.filter(email__startswith=re.split(r"@", email)[0]+r"@"):
            return True
        else:
            return False
    else:
        return False


def get_university_from_email(email):
    u = ValidEmail.objects.filter(email_extension=re.split(r"@", email)[-1])[0].universities
    if not u:
        return None
    else:
        return u


class UserPhoto(models.Model):
    user = models.ForeignKey(User)
    file_name = models.ImageField(upload_to='user_pictures/')
    title = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.file_name.path


