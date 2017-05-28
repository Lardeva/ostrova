# coding=utf-8
import logging

from django.http import HttpResponse

from clever_select_enhanced.views import ChainedSelectChoicesView
from nomenclature.models import Article, ArticleGroup, Supplier
from ostrovaweb.utils import nvl


def article_name_lookup(request):
    #field = request.GET['field']
    value = request.GET['value']

    article_text = ''
    try:
        article_text = str(Article.objects.get(id=value))
    except Article.NotFoundException:
        pass

    return HttpResponse(article_text)

class ArticleAjaxChainedView(ChainedSelectChoicesView):
    """
    View to handle the ajax request for the field options.
    """

    def get_choices(self, request):
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


class ArticleAjaxOrderChainedView(ChainedSelectChoicesView):
    """
    View to handle the ajax request for the field options.
    """

    def get_choices(self, request):
        vals_list = []
        ids_list = []

        # logging.error("field:" + self.field)
        # logging.error(u"parent_value:" + self.parent_value)
        # logging.error(u"parent2_value:" + str(self.add_rel_value))

        if self.field.endswith('price'):
            article = Article.objects.get(id=self.parent_value)
            vals_list = [nvl(article.sale_price,0),]
            ids_list = [nvl(article.sale_price,0),]

        # if self.field.endswith('hall_price'):
        #     article = Article.objects.get(id=self.parent_value).filter(article__group_fk=self.parent_value)
        #     vals_list = [nvl(article.order_price,0),]
        #     ids_list = [nvl(article.order_price,0),]

        return tuple(zip(ids_list, vals_list))

