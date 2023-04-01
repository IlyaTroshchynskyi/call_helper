from rest_framework.exceptions import ParseError


class Time15MinutesValidator:
    message = "The time must be a multiple of 15 minutes."

    def __call__(self, value):
        if not value:
            return
        if value.minute % 15 > 0:
            raise ParseError(self.message)
