#!/usr/bin/env python
import requests
from lxml import etree
from .field import BaseField


class ItemMeta(type):
    """
    Metaclass for a talonspider item.
    """

    def __new__(cls, name, bases, attrs):
        _fields = dict({(field_name, attrs.pop(field_name)) for field_name, object in list(attrs.items()) if
                        isinstance(object, BaseField)})
        _fields['spider_name'] = name.lower()
        attrs['_fields'] = _fields
        new_class = super(ItemMeta, cls).__new__(cls, name, bases, attrs)
        return new_class


class Item(metaclass=ItemMeta):
    """
    Item class for each item
    """

    def __init__(self, html):
        if html is None or not isinstance(html, etree._Element):
            raise ValueError("etree._Element is expected")
        for field_name, field_value in self._fields.items():
            get_field = getattr(self, 'tal_%s' % field_name, None)
            value = field_value.extract_value(html) if isinstance(field_value, BaseField) else field_value
            if get_field:
                value = get_field(value)
            setattr(self, field_name, value)

    @classmethod
    def _get_html(cls, url, params, **kwargs):
        response = requests.get(url, params, **kwargs)
        response.raise_for_status()
        return response.text

    @classmethod
    def get_item(cls, html='', url='', params=None, **kwargs):
        if html:
            html = etree.HTML(html)
        elif url:
            text = cls._get_html(url, params=params, **kwargs)
            html = etree.HTML(text)
        else:
            raise ValueError("html or url is expected")
        item = {}
        ins_item = cls(html=html)
        for i in cls._fields.keys():
            item[i] = getattr(ins_item, i)
        return item

    @classmethod
    def get_items(cls, html='', url='', params=None, **kwargs):
        pass
