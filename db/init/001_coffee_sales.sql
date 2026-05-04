create table if not exists coffee_sales (
    id bigserial primary key,
    hour_of_day integer not null check (hour_of_day between 0 and 23),
    cash_type text not null check (cash_type in ('card', 'cash')),
    money numeric(10, 2) not null check (money >= 0),
    coffee_name text not null,
    time_of_day text not null,
    weekday text not null,
    month_name text not null,
    weekdaysort integer not null check (weekdaysort between 1 and 7),
    monthsort integer not null check (monthsort between 1 and 12),
    sale_date date not null,
    sale_time time not null
);

copy coffee_sales (
    hour_of_day,
    cash_type,
    money,
    coffee_name,
    time_of_day,
    weekday,
    month_name,
    weekdaysort,
    monthsort,
    sale_date,
    sale_time
)
from '/data/coffee_sales.csv'
with (format csv, header true);

