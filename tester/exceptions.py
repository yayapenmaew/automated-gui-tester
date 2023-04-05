import boto3
import time
def storeToRunTestFailDB(appId, device, err):
    tableName = 'run-test-fail-app'
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    timestamp = time.time()
    readableTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
    response = table.put_item(
    Item={
        'appId':appId,
        'device':device,
        'err':err,
        'timestamp': readableTime
    }
)

class EXIT_CODE:
    UNKNOWN_ERROR = 1
    DEVICE_OFFLINE = 2
    DYNAMIC_TEST_ERROR = 10
    TIMEOUT_ERROR = 11
    PAID_APP_ERROR = 12
    NOT_SUPPORTED_ERROR = 13
    GAMES_CAT_ERROR = 14
    APP_NOT_FOUND_ERROR = 15
    ANALYZER_ERROR = 20
    EXTERNAL_INTERFACE_ERROR = 30
    BAD_INPUT_ERROR = 40
    ALREADY_TESTED_ERROR = 41
    DOWNLOAD = 43
    INSTALL_BUTTON = 44

class UnknownError(Exception):
    def __init__(self, message="Unknown error"):
        self.exit_code = EXIT_CODE.UNKNOWN_ERROR
        super().__init__(message)


class DeviceOfflineError(Exception):
    def __init__(self, message="The testing device is currently offline"):
        self.exit_code = EXIT_CODE.DEVICE_OFFLINE
        super().__init__(message)


class DynamicTestError(Exception):
    def __init__(self, appId, device, message="Unexpected error while performing dynamic test"):
        self.exit_code = EXIT_CODE.DYNAMIC_TEST_ERROR
        storeToRunTestFailDB(appId, device, message)
        super().__init__(message)


class TimeOutError(Exception):
    def __init__(self, appId, device, message="Tester took too long time to test"):
        self.exit_code = EXIT_CODE.TIMEOUT_ERROR
        storeToRunTestFailDB(appId, device, message)
        super().__init__(message)

class DownloadError(Exception):
    def __init__(self, appId, device, message="Can't download the application"): #press install > partially download laew but fail
        self.exit_code = EXIT_CODE.DOWNLOAD
        storeToRunTestFailDB(appId, device, message)
        super().__init__(message)

class PaidAppError(Exception):
    def __init__(self, appId, device, message="Could not test a paid application"):
        self.exit_code = EXIT_CODE.PAID_APP_ERROR
        storeToRunTestFailDB(appId, device, message)
        super().__init__(message)


class NotSupportedError(Exception):
    def __init__(self, appId, device, message="Could not test the application"):
        self.exit_code = EXIT_CODE.NOT_SUPPORTED_ERROR
        storeToRunTestFailDB(appId, device, message)
        super().__init__(message)


class GamesNotSupportedError(Exception):
    def __init__(self, appId, device, message="Game applications not supported"):
        self.exit_code = EXIT_CODE.GAMES_CAT_ERROR
        storeToRunTestFailDB(appId, device, message)
        super().__init__(message)


class AppNotFoundError(Exception):
    def __init__(self, appId, device, message="Application not found"):
        self.exit_code = EXIT_CODE.APP_NOT_FOUND_ERROR
        print(appId, device, message)
        storeToRunTestFailDB(appId, device, message)
        super().__init__(message)

class InstallButtonError(Exception):
    def __init__(self, appId, device, message="Could not find the install button."):
        self.exit_code = EXIT_CODE.INSTALL_BUTTON
        print(appId, device, message)
        storeToRunTestFailDB(appId, device, message)
        super().__init__(message)


class VULPIXAnalyzerError(Exception):
    def __init__(self, message="Error while analyzing the traffic"):
        self.exit_code = EXIT_CODE.ANALYZER_ERROR
        super().__init__(message)


class ExternalInterfaceError(Exception):
    def __init__(self, appId, device, message="Error while sending result to the external service"):
        self.exit_code = EXIT_CODE.EXTERNAL_INTERFACE_ERROR
        storeToRunTestFailDB(appId, device, message)
        super().__init__(message)


class BadInputError(Exception):
    def __init__(self, appId, device, message="Bad input error"):
        self.exit_code = EXIT_CODE.BAD_INPUT_ERROR
        storeToRunTestFailDB(appId, device, message)
        super().__init__(message)


class AlreadyTestedError(Exception):
    def __init__(self, appId, device, message="This version of the application is already tested"):
        self.exit_code = EXIT_CODE.ALREADY_TESTED_ERROR
        storeToRunTestFailDB(appId, device, message)
        super().__init__(message)


def resolve_exit_code(exit_code):
    exit_code_mapper = {
        EXIT_CODE.UNKNOWN_ERROR: UnknownError(),
        EXIT_CODE.DEVICE_OFFLINE: DeviceOfflineError(),
        EXIT_CODE.DYNAMIC_TEST_ERROR: DynamicTestError(),
        EXIT_CODE.TIMEOUT_ERROR: TimeOutError(),
        EXIT_CODE.PAID_APP_ERROR: PaidAppError(),
        EXIT_CODE.NOT_SUPPORTED_ERROR: NotSupportedError(),
        EXIT_CODE.GAMES_CAT_ERROR: GamesNotSupportedError(),
        EXIT_CODE.APP_NOT_FOUND_ERROR: AppNotFoundError(),
        EXIT_CODE.ANALYZER_ERROR: VULPIXAnalyzerError(),
        EXIT_CODE.EXTERNAL_INTERFACE_ERROR: ExternalInterfaceError(),
        EXIT_CODE.BAD_INPUT_ERROR: BadInputError(),
        EXIT_CODE.ALREADY_TESTED_ERROR: AlreadyTestedError(),
        EXIT_CODE.DOWNLOAD: DownloadError(),
        EXIT_CODE.INSTALL_BUTTON: InstallButtonError()
    }
    return exit_code_mapper[exit_code] if exit_code in exit_code_mapper else None