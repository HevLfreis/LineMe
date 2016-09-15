class LowCreditError(Exception):

    def __str__(self):
        return repr('Low Credits')
