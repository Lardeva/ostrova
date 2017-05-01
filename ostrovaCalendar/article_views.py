# coding=utf-8
import logging

from ostrovaCalendar.clever_select_enhanced.views import ChainedSelectChoicesView
from ostrovaCalendar.models import Article, ArticleGroup, Supplier
from ostrovaweb.utils import nvl


class ArticleAjaxChainedView(ChainedSelectChoicesView):
    """
    View to handle the ajax request for the field options.
    """

    def get_choices(self):
        vals_list = []
        ids_list = []


        logging.error("field:" + self.field)
        logging.error(u"parent_value:" + self.parent_value)
        logging.error(u"parent2_value:" + str(self.add_rel_value))

        if self.field.endswith('article_fk'):
            articles = Article.objects.filter(group_fk=self.parent_value).filter(supplier_fk=self.add_rel_value)
            vals_list = [x.name for x in articles]
            ids_list = [x.id for x in articles]

        if self.field.endswith('price'):
            article = Article.objects.get(id=self.parent_value)
            vals_list = [nvl(article.delivery_price,0),]
            ids_list = [nvl(article.delivery_price,0),]

        if self.field.endswith('group_fk'):
            supplier = Supplier.objects.get(id=self.parent_value)
            groups = ArticleGroup.objects.filter(article__supplier_fk=supplier)
            vals_list = [x.name for x in groups]
            ids_list = [x.id for x in groups]

        return tuple(zip(ids_list, vals_list))

