#!/usr/bin/env python
# encoding:utf-8


class GlobalVar(object):
    first_product_push_to_coop = False

    @staticmethod
    def set_push_status():
        GlobalVar.first_product_push_to_coop = True

    @staticmethod
    def get_push_status():
        return GlobalVar.first_product_push_to_coop
