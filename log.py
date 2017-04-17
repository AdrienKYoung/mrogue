import consts

_logger = open("log.txt","w")

def info(module,message,values):
    if module in consts.DEBUG_DETAIL_LOGGING:
        _logger.write("[INFO][{}] ".format(module) + message.format(*values) + "\n")

def warn(module,message,values):
    if module in consts.DEBUG_DETAIL_LOGGING:
        _logger.write("[WARN][{}] ".format(module) + message.format(*values) + '\n')

def error(module,message,values):
    _logger.write("[ERROR][{}] ".format(module) + message.format(*values) + '\n')
