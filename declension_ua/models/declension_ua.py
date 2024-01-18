from odoo import api, models
import pymorphy3


class DeclensionUA(models.AbstractModel):
    _name = 'declension.ua'
    _description = 'Declension for Ukrainian names'

    @api.model
    def _compute_inflected_field(self, value, grammatical_case):
        morph = pymorphy3.MorphAnalyzer(lang='uk')
        if isinstance(value, str):
            words = value.split()
            inflected_words = []
            for word in words:
                # Check if the word contains any numeric characters
                if any(char.isdigit() for char in word):
                    inflected_words.append(word)
                else:
                    parsed_word = morph.parse(word)[0].inflect({grammatical_case})
                    if parsed_word is not None:
                        inflected_words.append(parsed_word.word)
            return ' '.join(inflected_words)
        else:
            return value

    @api.model
    def get_declension_fields(self, record, grammatical_cases):
        inflected_fields = {}
        for grammatical_case in grammatical_cases:
            inflected_value = self._compute_inflected_field(record.name, grammatical_case)
            inflected_fields[f"name_{grammatical_case}"] = inflected_value
        return inflected_fields
