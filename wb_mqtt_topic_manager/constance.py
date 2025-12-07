class QosType:
    """Уровни гарантии доставки"""

    QOS_ZERO = 0
    QOS_ONE = 1
    QOS_TWO = 2


class ErrorType:
    """Типы ошибок согласно конвенции Wiren Board"""

    READ = 'r'
    WRITE = 'w'
    PERIOD = 'p'

    ERRORS = (READ, WRITE, PERIOD)
