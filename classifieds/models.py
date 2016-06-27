from django.db import models

from sorl.thumbnail import ImageField
from django.conf import settings

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from userena.models import UserenaBaseProfile

class MyProfile(UserenaBaseProfile):
    user = models.OneToOneField(User,
                                unique=True,
                                verbose_name=_('user'),
                                related_name='my_profile')
    phone = models.CharField(_('phone'), max_length=30, null=True, blank=True)
    secondary_email = models.EmailField(_('secondary email'), null=True)
    receive_news = models.BooleanField(_('receive news'), default=True, db_index=True)

class Section(models.Model):
    title = models.CharField(_('title'), max_length=100)

    def count(self):
        return Item.objects.filter(is_active=True)\
            .filter(group__section=self).count()

    class Meta:
        verbose_name = _('section')
        verbose_name_plural = _('sections')


class Group(models.Model):

    title = models.CharField(_('title'), max_length=100)
    section = models.ForeignKey('Section', verbose_name=_('section'))

    def count(self):
        return self.item_set.filter(is_active=True).count()

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')
        ordering = ['section__title', 'title', ]

    def get_title(self):
        return '%s' % self.title

class Item(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    group = models.ForeignKey(Group, verbose_name=_('group'))

    title = models.CharField(_('title'), max_length=100)
    description = models.TextField(_('description'))
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    phone = models.CharField(_('phone'), max_length=30)
    is_active = models.BooleanField(_('display'), default=True, db_index=True)
    updated = models.DateTimeField(_('updated'), auto_now=True, db_index=True)
    posted = models.DateTimeField(_('posted'), auto_now_add=True)

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')
        ordering = ('-updated', )


    def get_title(self):
        return '%s' % self.title

    def get_description(self):
        return '%s' % self.description[:155]

    def get_keywords(self):
        # TODO need more optimal keywords selection
        return ",".join(set(self.description.split()))

    def get_related(self):
        # TODO Need more complicated related select
        return Item.objects.exclude(pk=self.pk)[:settings.DCF_RELATED_LIMIT]


class Image(models.Model):
    item = models.ForeignKey(Item)
    file = ImageField(_('image'), upload_to='images')
