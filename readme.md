# Odoo Military App

[//]: # (disclaimer)

Disclaimer
----------
В модулях інтегровано демонстраційні дані. Будь-які збіги назв, прізвищ, імен, номерів телефонів та ІПН є випадковими.

При встановленні із демонстраційними даними необхідно у файлі конфігурації системи (.odoorc) встановити параметр limit_time_real не нижче 1200 через те, що тривалий час займає відмінювання назв підрозділів, посад та ПІБ у різних відмінках.

[//]: # (end disclaimer)
[//]: # (addons)
Available addons
----------------
| addon                                                | summary                    | description                |
|------------------------------------------------------|----------------------------|----------------------------|
| [declension_ua](declension_ua/readme.md)             | Ukrainian names declension | Ukrainian names declension |
| [military_app](military_app/readme.md)               | Military App               | Military App               |
| [military_company](military_company/readme.md)       | Military Company           | Military Company data      |
| [military_department](military_department/readme.md) | Military Department        | Military Departments Data  |
| [military_employee](military_employee/readme.md)     | Military Employee          | Military Employee Data     |
| [military_job](military_job/readme.md)               | Military Job               | Military Job Data          |
| [military_rank](military_rank/readme.md)             | Military Rank              | Military Ranks Data        |
|

[//]: # (end addons)

[//]: # (todo)
TODO
----
1. Призначення на ТВО (тимчасово виконуючого обовʼязки) посади.
2. Визначення ієрархій посад. Командир / перший заступник / другий заступник / третій заступник. Потрібно для подальшого визначення ТВО (тимчасово виконуючого обовʼязки).
3. Облік переміщення військовослужбовців:
   - використання частини функціоналу модуля stock (stock.location);
   - реалізація на зразок переміщення товару по розміщеннях;
4. Облік служб у в/ч:
   - начальник/командир служби (для подальшого використання при формуванні звітів);
   - розділи в меню для служб для обліку за напрямком роботи служби;

[//]: # (end todo)
