{
    "name": "declension_ua",
    "version": "1.0",
    "summary": "Ukrainian names declension with pymorphy2 library",
    "description": """To use declension in your module you should do the following:
                   1. Add this module in your module dependency list
                   2. Add field to your module with name_declension name where declension is:
                   - ablt - Ablative;
                   - gent - Genitive;
                   - datv - Dative;
                   (for example name_datv)
                   3. Your field should 
                   """,
    "category": "Tools",
    "author": "Yevhen Babii",
    "website": "Website",
    "license": "Other proprietary",
    "external_dependencies": {
        "python": ["pymorphy3",
                   "pymorphy3-dicts-uk",
                   # "pymorphy2", # In case of using pymorphy2 library
                   # "pymorphy2_dicts_uk",
                   # "js2py", # TODO: Test and implement shevchenko-js library
                   ],
        # "javascript": ["shevchenko"], # TODO: Test and implement shevchenko-js library
    },
    "installable": True,
    "auto_install": True
}
