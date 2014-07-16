from jsonfield import JSONField
import json


class JSONFieldUtf8(JSONField):

    def dumps_for_display(self, value):
        kwargs = {"indent": 2}
        kwargs.update(self.dump_kwargs)
        return json.dumps(value, ensure_ascii=False, **kwargs).encode('utf-8')

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^wanglibao\.fields\.JSONFieldUtf8"])
