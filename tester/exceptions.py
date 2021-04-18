class EXIT_CODE:
    DYNAMIC_TEST_ERROR = 10
    TIMEOUT_ERROR = 11
    PAID_APP_ERROR = 12
    ANALYZER_ERROR = 20
    EXTERNAL_INTERFACE_ERROR = 30
    BAD_INPUT_ERROR = 40

class DynamicTestError(Exception):
    def __init__(self, message="Unexpected error while performing dynamic test"):
        self.exit_code = EXIT_CODE.DYNAMIC_TEST_ERROR
        super().__init__(message)


class TimeOutError(Exception):
    def __init__(self, message="Tester took too long time to test"):
        self.exit_code = EXIT_CODE.TIMEOUT_ERROR
        super().__init__(message)


class PaidAppError(Exception):
    def __init__(self, message="Could not test a paid application"):
        self.exit_code = EXIT_CODE.PAID_APP_ERROR
        super().__init__(message)


class VULPIXAnalyzerError(Exception):
    def __init__(self, message="Error while analyzing the traffic"):
        self.exit_code = EXIT_CODE.ANALYZER_ERROR
        super().__init__(message)


class ExternalInterfaceError(Exception):
    def __init__(self, message="Error while sending result to the external service"):
        self.exit_code = EXIT_CODE.EXTERNAL_INTERFACE_ERROR
        super().__init__(message)

class BadInputError(Exception):
    def __init__(self, message="Bad input error"):
        self.exit_code = EXIT_CODE.BAD_INPUT_ERROR
        super().__init__(message)

def resolve_exit_code(exit_code):
    exit_code_mapper = {
        EXIT_CODE.DYNAMIC_TEST_ERROR: DynamicTestError(),
        EXIT_CODE.TIMEOUT_ERROR: TimeOutError(),
        EXIT_CODE.PAID_APP_ERROR: PaidAppError(),
        EXIT_CODE.ANALYZER_ERROR: VULPIXAnalyzerError(),
        EXIT_CODE.EXTERNAL_INTERFACE_ERROR: ExternalInterfaceError(),
        EXIT_CODE.BAD_INPUT_ERROR: BadInputError(),
    }
    return exit_code_mapper[exit_code] if exit_code in exit_code_mapper else None