from Attributes.Attribute import Attribute


class MonthAttribute(Attribute):
    def __init__(self):
        super().__init__()
        self.pattern = '[MONTH]'

    def generate_attr(self, obj, noun_mod_occurrences, named_entities_dist):
        month_facts = {}
        dates = named_entities_dist['DATE']
        for date in dates:
            month = self.__has_month(date)
            if month:
                month_facts[month] = month_facts.get(month, 0) + dates[date]
        return month_facts

    def __has_month(self, s):
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        for month in months:
            if month.lower() in s.lower():
                return month
        return ''
