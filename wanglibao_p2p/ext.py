# encoding: utf-8
from datetime import datetime
import json
from django.db import models
from django.utils.six import with_metaclass


class P2PTerm(object):

    date_format = '%Y-%m-%d'

    def __init__(self, _date, paid=False, delay=False):
        self.term_date = _date
        self.paid = paid
        self.delay = delay

    @classmethod
    def from_json(cls, json_string):
        data = json.loads(json_string)
        term_date = datetime.strptime(data['date'], cls.date_format)
        paid = data['paid']
        delay = data['delay']
        return P2PTerm(term_date, paid, delay)

    def to_json(self):
        return json.dumps(self.serializer())

    @property
    def status(self):
        if self.paid and (not self.delay):
            return u'已还'
        if (not self.paid) and self.delay:
            return u'逾期未还'
        if self.paid and self.delay:
            return u'逾期已还'
        if (not self.paid) and (not self.delay):
            return u'未到还款期限'

    def serializer(self):
        return {
            'date': self.term_date.strftime(self.date_format),
            'paid': self.paid,
            'delay': self.delay
        }


class P2PPeriod(object):

    date_format = '%Y-%m-%d'

    def __init__(self, term_list):
        for term in term_list:
            if not isinstance(term, P2PTerm):
                raise TypeError('')
        self.terms = term_list

    @property
    def count(self):
        return len(self.terms)

    @classmethod
    def to_date(cls, date_string_list):
        return [datetime.strptime(date_string, cls.date_format).date() for date_string in date_string_list]

    def serializer(self):
        terms = list()
        for term in self.terms:
            terms.append(term.serializer())
        return {
            'count': self.count,
            'terms': terms
        }

    @classmethod
    def from_json(self, json_string):
        data = json.dumps(json_string)
        terms = data['terms']
        return P2PPeriod(terms)

    def to_json(self):
        return json.dumps(self.serializer())


class AmoDateField(with_metaclass(models.SubfieldBase, models.Field)):

    description = u'Store list of amortizations.'

    def get_internal_type(self):
        return "TextField"

    def to_python(self, value):
        if isinstance(value, P2PPeriod):
            return value
        return P2PPeriod.from_json(value)

    def get_prep_value(self, value):
        return value.to_json()



