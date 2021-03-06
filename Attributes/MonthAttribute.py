from Attributes.Attribute import Attribute


class MonthAttribute(Attribute):
    """
    Attribute that outputs month attribute
    """
    def __init__(self, get_prev=False):
        super().__init__(get_prev)
        self.pattern = '[MONTH]'
        self.month_facts = {}

    def generate_attr(self, obj: str, noun_mod_occurrences: dict, named_entities_dist: dict):
        # to remove repetitive selection of DATE entity
        if self.month_facts:
            return self.month_facts

        month_facts = {}
        dates = named_entities_dist['DATE']
        for date in dates:
            month = self.__has_month(date)
            if month:
                month_facts[month] = month_facts.get(month, 0) + dates[date]

        self.month_facts = month_facts

        return month_facts

    def __has_month(self, s: str):
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        for month in months:
            if month.lower() in s.lower():
                return month
        return ''
