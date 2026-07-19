import logging


class IgnoreHealthCheckFilter(logging.Filter):
    def filter(self, record):
        return "/api/health/" not in record.getMessage()
