# coding=utf-8
import logging

from ostrovaCalendar.clever_select_enhanced.views import ChainedSelectChoicesView
from ostrovaCalendar.models import Article


class ArticleAjaxChainedView(ChainedSelectChoicesView):
    """
    View to handle the ajax request for the field options.
    """

    def get_choices(self):
        vals_list = []
        ids_list = []

        logging.error("field:" + self.field)
        logging.error(u"parent_value:" + self.parent_value)

        if self.field.endswith('article_fk'):
            articles = Article.objects.filter(group_fk=self.parent_value)
            vals_list = [x.name for x in articles]
            ids_list = [x.id for x in articles]

        return tuple(zip(ids_list, vals_list))

