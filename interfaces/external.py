import requests as req
import json

fieldNameMapper = {
    "Advertiser ID": "advertiserId",
    "Android ID": "androidId",
    "Device Serial Number": "deviceSerialNumber",
    "Google Services Framework ID": "googleServicesId",
    "IMEI": "imei",
    "MAC Address": "macAddress",
    "Cell ID": "cellId",
    "ICCID (SIM serial number)": "simSerialNumber",
    "IMSI": "imsi",
    "Location Area Code": "localAreaCode",
    "Phone Number": "phoneNumber",
    "Age": "age",
    "Audio Recording": "audioRecording",
    "Calendar": "calendar",
    "Contract Book": "contactBook",
    "Country": "country",
    "Credit Card CCV": "ccv",
    "Date Of Birth": "dob",
    "Email": "email",
    "Gender": "gender",
    "Name": "name",
    "Password": "password",
    "Photo": "photo",
    "Physical Address": "physicalAddress",
    "Relationship Status": "relationshipStatus",
    "SMS Message": "sms",
    "SSN": "ssn",
    "Time Zone": "timezone",
    "Username": "username",
    "Video": "video",
    "Web Browsing Log": "webBrowsingLog",
    "GPS (current latitude and longitude)": "gps",
}


class ExternalOutputInterface:
    def __init__(self, endpoint=None):
        self.endpoint = endpoint

    def __send_request(self, payload):
        if self.endpoint:
            res = req.post(self.endpoint, json=payload)
        else:
            print(json.dumps(payload))

    def create_app_info_payload(self, app_id, app_name, dev_name, icon_url, category):
        return {
            "identifier": app_id,
            "name": app_name,
            "devName": dev_name,
            "iconUrl": icon_url,
            "categorySlug": category,
        }

    def create_result_payload(self, app_id, app_version, android_version, score, PI_result):
        converted_result = {
            "applicationId": app_id,
            "version": app_version,
            "androidVersion": android_version,
            "vulpixScore": score,
        }

        for PI in PI_result:
            converted_result[fieldNameMapper[PI]] = bool(PI_result[PI])

        return converted_result

    def send_error(exception):
        payload = { 
            "status": "error",
            "error": exception.__class__.__name__
        }

        self.send_request(payload)

    def send_result(self, app_id, app_name, app_version, android_version, score, PI_result, dev_name, icon_url, category, log_path):
        app_info = self.create_app_info_payload(
            app_id,
            app_name,
            dev_name,
            icon_url,
            category,
        )

        result = self.create_result_payload(
            app_id,
            app_version,
            android_version,
            score,
            PI_result,
        )

        payload = {
            "status": "success",
            "appInfo": app_info,
            "result": result,
            "logs": log_path,
        }

        self.__send_request(payload)

        return payload
