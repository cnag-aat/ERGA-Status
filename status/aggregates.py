from django.db.models import Aggregate, CharField

class GroupConcat(Aggregate):
    function = "GROUP_CONCAT"
    allow_distinct = True
    template = "%(function)s(%(distinct)s%(expressions)s%(ordering)s SEPARATOR '%(separator)s')"

    def __init__(
        self,
        expression,
        distinct=False,
        ordering=None,
        separator="; ",
        **extra,
    ):
        super().__init__(
            expression,
            distinct="DISTINCT " if distinct else "",
            ordering=f" ORDER BY {ordering}" if ordering else "",
            separator=separator,
            output_field=CharField(),
            **extra,
        )