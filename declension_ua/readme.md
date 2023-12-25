# Ukrainian names declension

Опис:
------------
Модуль реалізовано на основі бібліотеки pymorphy2 та українського словника pymorphy2_dicts_uk до нього.
Для застосування необхідно:
1. Додати даний модуль в залежності Вашого модуля.
2. В коді модуля створити необхідні відмінювані поля/поле: з наступними можливими назвами:
name_gent = fields.Char(string="Name Genitive", compute="_get_declension")
name_datv = fields.Char(string="Name Dative", compute="_get_declension")
name_ablt = fields.Char(string="Name Ablative", compute="_get_declension")
3. Додати в модуль наступний код:
    @api.depends('name')
    def _get_declension(self):
        declension_ua_model = self.env['declension.ua']
        grammatical_cases = ['gent', 'datv', 'ablt']
        for record in self:
            inflected_fields = declension_ua_model.get_declension_fields(record, grammatical_cases)
            for field, value in inflected_fields.items():
                setattr(record, field, value)

ToDo
----


[//]: # (end todo)
