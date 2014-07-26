from rest_framework import serializers


class ModelSerializerExtended(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        self.request = None
        super(ModelSerializerExtended, self).__init__(*args, **kwargs)

    def get_default_fields(self):
        fields = super(ModelSerializerExtended, self).get_default_fields()
        request = self.context.get('request', None)
        if request is not None:
            self.request = request
            fields_param = request.QUERY_PARAMS.get('fields', None)

            if fields_param:
                fields_to_remove = set(fields.keys()) - set(fields_param.split(','))
            else:
                fields_to_remove = set()

            fields_to_remove |= set(request.QUERY_PARAMS.get('exclude', '').split(','))

            for field in fields_to_remove:
                if field in fields:
                    fields.pop(field)

        return fields