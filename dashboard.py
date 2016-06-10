from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools.utils import get_admin_site_name

from admin_tools.menu import items, Menu

from shop.views import OrdersModule

class CustomMenuDashboard(Menu):
	def init_with_context(self, context):
		site_name = get_admin_site_name(context)
		self.children += [
			items.MenuItem(_('Dashboard'), '/%s/' %site_name),
			items.Bookmarks(),
			items.AppList(
				_('Applications'),
				exclude=(
					'django.contrib.*',
					'parsers.*',
					'pay.models.*',
					'sms.models.*',
					'project.models.*',
				)
			),
			
			items.AppList(
				_('Administration'),
				models=(
					'django.contrib.*',
					'pay.models.*',
					'sms.models.*',
				)
			),
			
			items.MenuItem(_('Parsers'),
				children=[
					items.MenuItem(_('Exelparser'), '/admin/exelparser/exelparserfile/'),
				]
			),
			
			items.MenuItem(_('Report'), '/admin/shop/report/'),
			
			items.MenuItem(_('Translation'),
				children=[
					items.MenuItem(_('Interface'), '/admin/project/translateinterface/'),
					items.MenuItem(_('Additionally'), '/rosetta/'),
				]
			),
		]

class CustomIndexDashboard(Dashboard):
	"""
	Custom index dashboard for www.
	"""
	def init_with_context(self, context):
		site_name = get_admin_site_name(context)
		
		self.children.append(OrdersModule())

		self.children.append(modules.Group(
			title=_('Content'),
			display="tabs",
			children=[
				modules.AppList(
					title=_('Shop'),
					models=(
						'shop.models.Category',
						'shop.models.Product',
						'shop.models.Order',
						'shop.models.Printer',
						'shop.models.OrderStatus',
					)
                ),
				modules.AppList(
                    title=_('Users messages'),
                    models=(
						'questionanswer.models.*',
						'feedback.models.*',
					)
                ),
				modules.AppList(
                    title=_('Actions'),
                    models=(
						'actions.models.*',
					)
                ),
				modules.AppList(
                    title=_('Other pages'),
                    models=(
						'my_flatpages.models.*',
					)
                ),
            ]
		))
		
		# if context['request'].user.is_superuser:
			# from parsers.pparser.views import PparserModule
			# self.children.append(PparserModule())
		
		# append a link list module for "filebrowser"
		self.children.append(modules.LinkList(
			_('FileBrowser'),
			children=[
				[_('FileBrowser'), '/admin/filebrowser/browse/'],
			]
		))
		
		# append a link list module for "quick links"
		self.children.append(modules.LinkList(
			_('Quick links'),
			layout='inline',
			children=[
				[_('Return to site'), '/'],
				[_('Change password'),'/admin/password_change/'],
				[_('Log out'), '/admin/logout/'],
			]
		))

        # append a recent actions module
		self.children.append(modules.RecentActions(_('Recent Actions'), 5))
		
		if context['request'].user.is_superuser:
			from configuration.views import ConfigModule
			self.children.append(ConfigModule())


class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for www.
    """

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(_(self.app_title), self.models),
            modules.RecentActions(
                _('Recent Actions'),
                include_list=self.get_app_content_types(),
                limit=5
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomAppIndexDashboard, self).init_with_context(context)
