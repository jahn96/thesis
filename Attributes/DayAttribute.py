from Attributes.Attribute import Attribute


class DayAttribute(Attribute):
    def __init__(self):
        super().__init__()
        self.pattern = '[DAY]'
        self.day_facts = {}

    def generate_attr(self, obj, noun_mod_occurrences, named_entities_dist):
        if self.day_facts:
            return self.day_facts

        day_facts = {}
        dates = named_entities_dist['DATE']
        for date in dates:
            day = self.__has_day(date)
            if day:
                day_facts[day] = day_facts.get(day, 0) + dates[date]

        self.day_facts = day_facts
        return day_facts

    def __has_day(self, s):
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        for day in days:
            if day.lower() == s.lower():
                return day
        return ''
