from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.db import models
from tagging.fields import TagField
from tagging.models import Tag
from tools.mixins import RateClassMixin, RateableMixin
from tools.decorators import extend
from blogging.exceptions import AlreadySubscribedError, NotSubscribedError


class BlogRate(RateClassMixin):
    """Rates for blog model"""
    enemy = models.ForeignKey('Blog', verbose_name=_('blog'))

    class Meta:
        verbose_name = _('BlogRate')
        verbose_name_plural = _('BlogRates')

    def __unicode__(self):
        return unicode(self.enemy)


class Blog(RateableMixin):
    """Blog model"""
    __rateclass__ = BlogRate

    name = models.CharField(max_length=300, verbose_name=_('name'))
    description = models.TextField(verbose_name=_('description'))
    author = models.ForeignKey(User, verbose_name=_('author'))

    class Meta:
        verbose_name = _('Blog')
        verbose_name_plural = _('Blogs')

    def __unicode__(self):
        return self.name


class PostRate(RateClassMixin):
    """Rates for post model"""
    enemy = models.ForeignKey('Post', verbose_name=_('post'))

    class Meta:
        verbose_name = _('PostRate')
        verbose_name_plural = _('PostRates')

    def __unicode__(self):
        return unicode(self.enemy)


class Post(RateableMixin):
    """Post model"""
    __rateclass__ = PostRate

    title = models.CharField(max_length=300, verbose_name=_('title'))
    preview = models.TextField(verbose_name=_('preview'))
    content = models.TextField(verbose_name=_('content'))
    blog = models.ForeignKey(Blog, null=True, verbose_name=_('blog'))
    tags = TagField(blank=True, null=True, verbose_name=_('tags'))
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created'),
    )
    updated = models.DateTimeField(
        auto_now=True, verbose_name=_('updated'),
    )
    is_draft = models.BooleanField(
        default=False, verbose_name=_('is draft'),
    )
    is_attached = models.BooleanField(
        default=False, verbose_name=_('is attached'),
    )
    is_commenting_locked = models.BooleanField(
        default=False, verbose_name=_('is commenting locked'),
    )

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def __unicode__(self):
        return self.title

    def subscribe(self, user):
        """Subscribe user to post"""
        if self.is_subscribed(user):
            raise AlreadySubscribedError(self)
        user.subscriptions.add(self)

    def unsubscribe(self, user):
        """Unsubscribe user from post"""
        if not self.is_subscribed(user):
            raise NotSubscribedError(self)
        user.subscriptions.remove(self)

    def is_subscribed(self, user):
        """Check user is subscribed to post"""
        return bool(user.subscriptions.filter(id=self.id).count())


@extend(User)
class Profile(object):
    """Extended profile for blogging"""
    subscriptions = models.ManyToManyField(Post, 
        related_name='sub_users', verbose_name=_('subscriptions'),
    )
    stars = models.ManyToManyField(Post,
        related_name='star_users', verbose_name=_('subscriptions'),
    )    
