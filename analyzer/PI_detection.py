import datetime
import os
import subprocess
import time
import errno
import time
import ast
import json
import re
import pandas as pd
import pycountry
import sys
import logging

from ijson.common import ObjectBuilder
from subprocess import Popen, PIPE
from multiprocessing import Pool, Lock

result_folder = "../result"

class PI_GROUP:
    DEVICE = "device"
    SIMCARD = "simcard"
    USER = "user"
    LOCATION = "location"

# PI elements that we are interest

PII_TYPE = {
    "Advertiser ID": { "group": PI_GROUP.DEVICE, "impact": True },
    "Android ID": { "group": PI_GROUP.DEVICE, "impact": True },
    "Device Serial Number": { "group": PI_GROUP.DEVICE, "impact": True },
    "Google Services Framework ID": { "group": PI_GROUP.DEVICE, "impact": True },
    "IMEI": { "group": PI_GROUP.DEVICE, "impact": True },
    "MAC Address": { "group": PI_GROUP.DEVICE, "impact": True },
    "Cell ID": { "group": PI_GROUP.SIMCARD, "impact": True },
    "ICCID (SIM serial number)": { "group": PI_GROUP.SIMCARD, "impact": True },
    "IMSI": { "group": PI_GROUP.SIMCARD, "impact": True },
    "Location Area Code": { "group": PI_GROUP.SIMCARD, "impact": True },
    "Phone Number": { "group": PI_GROUP.SIMCARD, "impact": True },
    "Age": { "group": PI_GROUP.USER, "impact": False },
    "Audio Recording": { "group": PI_GROUP.USER, "impact": False },
    "Calendar": { "group": PI_GROUP.USER, "impact": False },
    "Contract Book": { "group": PI_GROUP.USER, "impact": False },
    "Country": { "group": PI_GROUP.USER, "impact": False },
    "Credit Card CCV": { "group": PI_GROUP.USER, "impact": True },
    "Date Of Birth": { "group": PI_GROUP.USER, "impact": False },
    "Email": { "group": PI_GROUP.USER, "impact": True },
    "Gender": { "group": PI_GROUP.USER, "impact": False },
    "Name": { "group": PI_GROUP.USER, "impact": True },
    "Password": { "group": PI_GROUP.USER, "impact": False },
    "Photo": { "group": PI_GROUP.USER, "impact": False },
    "Physical Address": { "group": PI_GROUP.USER, "impact": True },
    "Relationship Status": { "group": PI_GROUP.USER, "impact": False },
    "SMS Message": { "group": PI_GROUP.USER, "impact": False },
    "SSN": { "group": PI_GROUP.USER, "impact": True },
    "Time Zone": { "group": PI_GROUP.USER, "impact": False },
    "Username": { "group": PI_GROUP.USER, "impact": False },
    "Video": { "group": PI_GROUP.USER, "impact": False },
    "Web Browsing Log": { "group": PI_GROUP.USER, "impact": False },
    "GPS (current latitude and longitude)": { "group": PI_GROUP.LOCATION, "impact": False },
}


Unique_username = "Sylphsgt098VWE"
Unique_password = "u8zvTBYNnnGn"
Email = "boomngongseniorproject@gmail.com"
Unspecified_text = "YaaKcuMEgEsr"
PhoneNo = "+66825999999"
firstname = "iBvAdkFi"
lastname = "eTJexjgnzPGS"
Country = "Thailand"
Province = "Bangkok"
Day = "29"
Month = "02"
Year = "1990"
FULLNAME = firstname + " " + lastname
Card = "5105105105105100"
Expir = "1225"
CVV = "122"
Postal = "10530"
CreditCardCVV = Card + Expir + CVV

DOB = Day + Month + Year


class VULPIXAnalyzer():
    def isEmail(PostData):
        EMAIL_PATTERN = r"^[_A-Za-z0-9-\\+]+((\\.|_)[_A-Za-z0-9-]+)*@" + \
            "[A-Za-z0-9-]+(\\.[A-Za-z0-9]+)*(\\.[A-Za-z]{2,})"
        EMAIL_temp = re.compile(EMAIL_PATTERN)
        x = EMAIL_temp.search(PostData)
        if(x != None):
            return True
        return False

    # including Audio/video

    def isVideo(PostData):
        PostData = PostData.lower()
        FILE_PATTERN = r"((.+\.)(webm|mpg|mp2|mpeg|mpe|mpv|ogg|mp4|m4p|m4v|avi|wmv|mov|qt|flv|swf|avchd))"
        FILE_PATTERN_temp = re.compile(FILE_PATTERN)
        x = FILE_PATTERN_temp.search(PostData.lower())
        if(x != None):
            return True
        return False

    def isAudio(PostData):
        PostData = PostData.lower()
        FILE_PATTERN = r"((.+\.)(mp3|wma|wav|mp2|aac|ac3|au|ogg|flac))"
        FILE_PATTERN_temp = re.compile(FILE_PATTERN)
        x = FILE_PATTERN_temp.search(PostData.lower())
        if(x != None):
            return True
        return False

    def isPhoto(PostData):
        PostData = PostData.lower()
        FILE_PATTERN = r"((.+\.)(jpg|png|ico|gif|bmp|jpeg))"
        FILE_PATTERN_temp = re.compile(FILE_PATTERN)
        x = FILE_PATTERN_temp.search(PostData.lower())
        if(x != None):
            return True
        return False

    def isLocationGPS(PostData):
        PostData = PostData.upper()
        temp_list = re.findall(r'[^\w\s]+|\w+', PostData)
        Loc_list = ["LAT", "LONG", "LNG", "LATITUDE",
                    "LONGITUDE", "LATLONG", "GPS", "COORDINATES", "LOC"]
        for latlong in Loc_list:
            if latlong in temp_list:
                return True
            return False

    def isIP(PostData):
        PostData = PostData.lower()
        ipv4Pattern = r"(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.){3}([01]?\\d\\d?|2[0-4]\\d|25[0-5])"
        ipv6Pattern = r"([0-9a-f]{1,4}:){7}([0-9a-f]){1,4}"

        ipv4Pattern_temp = re.compile(ipv4Pattern)
        ipv6Pattern_temp = re.compile(ipv6Pattern)

        x = ipv4Pattern_temp.search(PostData)
        y = ipv6Pattern_temp.search(PostData)
        if x != None or y != None:
            return True
        return False

    def isAdId(PostData):
        PostData = PostData.lower()
        AdIdPattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
        AdIdPattern_temp = re.compile(AdIdPattern)
        x = AdIdPattern_temp.search(PostData)
        if(x != None):
            #         print(x.group())
            return True
        return False

    def isTimeZone(PostData):
        PostData = PostData.upper()
        TimeZonePattern = r"^((19|20)[0-9][0-9])[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])[T]([01][1-9]|[2][0-3])[:]([0-5][0-9])[:]([0-5][0-9])([+|-]([01][0-9]|[2][0-3])[:]([0-5][0-9])){0,1}"
        TimeZonePattern_temp = re.compile(TimeZonePattern)
        x = TimeZonePattern_temp.search(PostData)
        if(x != None):
            return True
        return False

    def isDOB(PostData):
        DOBPattern = r"^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]|(?:Jan|Mar|May|Jul|Aug|Oct|Dec)))\1|(?:(?:29|30)(\/|-|\.)(?:0?[1,3-9]|1[0-2]|(?:Jan|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)(?:0?2|(?:Feb))\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9]|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep))|(?:1[0-2]|(?:Oct|Nov|Dec)))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})"
        DOBPattern_temp = re.compile(DOBPattern)
        x = DOBPattern_temp.search(PostData)
        if(x != None):
            return True
        return False

    def isCountry(PostData):
        PostData = PostData.upper()
        temp_list = re.findall(r'[^\w\s]+|\w+', PostData)

        TH_country_list = ["BANGKOK", "TH", "THA", "TH_TH", "ASIA"]
        for country_code in TH_country_list:
            if country_code in temp_list:
                return True
            return False

    def isMACAddr(PostData, MacAddr):

        mac_list = MacAddr.split(":")

        m0 = mac_list[0]
        m1 = mac_list[1]
        m2 = mac_list[2]
        m3 = mac_list[3]
        m4 = mac_list[4]
        m5 = mac_list[5]

        PostData = PostData.upper()
        temp_list = re.findall(r'[^\w\s]+|\w+', PostData)

        if (m0 in temp_list) and (m1 in temp_list) and (m2 in temp_list) and (m3 in temp_list) and (m4 in temp_list) and (m5 in temp_list):
            return True
        return False

    def setupPI(PI_file_path):
        # setup PI
        PI_info = open(PI_file_path, "r", encoding="ISO-8859-1")
        data = PI_info.read()
        json_pi = json.loads(data)
        Serial = json_pi["Serial"]
        PI_DICT = {Unique_username: "Username",
                   Unique_password: "Password",
                   Email: "Email",
                   PhoneNo: "Phone Number",
                   firstname: "Name",
                   lastname: "Name",
                   Country: "Country",
                   Province: "Physical Address",
                   DOB: "Date Of Birth",
                   CreditCardCVV: "Credit Card CCV",
                   Postal: "Physical Address",
                   Serial: "Device Serial Number",
                   "+07:00": "Time Zone"
                   }

        for i in json_pi:
            if "IMEI" in i:
                PI_DICT[json_pi[i]] = "IMEI"
            else:
                PI_DICT[json_pi[i]] = i
            if "MAC Address" in i:
                MacAddr = json_pi[i]

        return PI_DICT, MacAddr

    def getBackgroundTraffic():
        # Backgroud traffic
        Backgroud_Traffic = set()

        try:
            bg_traffic_path = "backgroundtraffic/"+device+".har"
            file_log = open(bg_traffic_path, "r", encoding="ISO-8859-1")
            data = file_log.read()
            json_body = json.loads(data)

            for i in json_body["log"]['entries']:
                temp_url = i['request']['url']
                temp = temp_url.split("//")
                url = temp[1].split("/")[0]
                Backgroud_Traffic.add(url)
        except:
            logging.warning(
                "Background traffic not found, using the default list instead.")

        temp_list_bg = ['graph.facebook.com',
                        'play.googleapis.com',
                        'android.googleapis.com',
                        'www.googleapis.com',
                        'android.clients.google.com',
                        'connectivitycheck.gstatic.com',
                        'clients3.google.com']

        for bg in temp_list_bg:
            Backgroud_Traffic.add(bg)
        return Backgroud_Traffic

    def score(PI_result):
        leaks_by_group = {
            PI_GROUP.DEVICE: 0,
            PI_GROUP.SIMCARD: 0,
            PI_GROUP.USER: 0,
            PI_GROUP.LOCATION: 0,
        }
        for PI_element in PII_TYPE:
            pi_group = PII_TYPE[PI_element]['group']
            ''' Full 25 points for high impact PI '''
            high_impact = PII_TYPE[PI_element]['impact']
            if high_impact and PI_result[PI_element]:
                leaks_by_group[pi_group] += 4
            else:
                leaks_by_group[pi_group] += PI_result[PI_element]

        VULPIX_score = 0
        for group in leaks_by_group:
            if leaks_by_group[group] > 4:
                VULPIX_score += 25
            else:
                VULPIX_score += leaks_by_group[group] / 4 * 25
        return VULPIX_score

    def analyze(package_name, PI_file_path="./analyzer/PI.json", har_file=None):
        logging.info(f"Analyzing traffic of {package_name}")
        result_dict = dict()

        for PI_element in PII_TYPE:
            result_dict[PI_element] = 0    

        Backgroud_Traffic = VULPIXAnalyzer.getBackgroundTraffic()
        PI_DICT, MacAddr = VULPIXAnalyzer.setupPI(PI_file_path)

        if not har_file:
            har_file = f"result/{package_name}.har"

        try:
            file_log = open(har_file, "r", encoding="ISO-8859-1")
            data = file_log.read()
            json_body = json.loads(data)
            Packets = json_body["log"]["entries"]
            packagename = package_name
            Entries_size = len(Packets)

            if not Packets:
                # No packet detected by the proxy.
                return 0, result_dict

            startTime = Packets[0]["startedDateTime"]
            found_PI = False

            for i in range(Entries_size):
                if found_PI:

                    utc_datetime_start = startTime.split("T")[1]
                    utc_datetime_found = found_PI_time.split("T")[1]
                    utc_datetime_start = utc_datetime_start.split('.')[
                        0]
                    utc_datetime_found = utc_datetime_found.split('.')[
                        0]

                    utc_datetime_start = utc_datetime_start.split(':')[
                        1]
                    utc_datetime_found = utc_datetime_found.split(':')[
                        1]

                    print(int(utc_datetime_found) -
                          int(utc_datetime_start))
                    break

                request = Packets[i]["request"]
                url = request["url"]
                temp = url.split("//")
                domain = temp[1].split("/")[0]

                ######### filtered backgroud traffic ######
                if domain not in Backgroud_Traffic:
                    # check PI (string matching)
                    for PI in PI_DICT:
                        if PI.lower() in str(request).lower():
                            result_dict[PI_DICT[PI]] = 1
                            found_PI_time = Packets[i]["startedDateTime"]
                            found_PI = True

                    # Check PI (Pattern matching)
                    header = request["headers"]
                    for entries in header:

                        if "content-disposition" in entries["name"].lower():

                            if(VULPIXAnalyzer.isVideo(entries["value"])):
                                result_dict["Video"] = 1
                                found_PI_time = Packets[i]["startedDateTime"]
                                found_PI = True

                            if(VULPIXAnalyzer.isAudio(entries["value"])):
                                result_dict["Audio Recording"] = 1
                                found_PI_time = Packets[i]["startedDateTime"]
                                found_PI = True

                            if(VULPIXAnalyzer.isPhoto(entries["value"]) or isPhoto(entries["value"])):
                                result_dict["Photo"] = 1
                                found_PI_time = Packets[i]["startedDateTime"]
                                found_PI = True

                    if(VULPIXAnalyzer.isEmail(str(request).lower())):
                        result_dict["Email"] = 1
                        found_PI_time = Packets[i]["startedDateTime"]
                        found_PI = True
                    if(VULPIXAnalyzer.isLocationGPS(str(request).lower())):
                        result_dict["GPS (current latitude and longitude)"] = 1
                        found_PI_time = Packets[i]["startedDateTime"]
                        found_PI = True

                    if(VULPIXAnalyzer.isMACAddr(str(request).lower(), MacAddr)):
                        result_dict["MAC Address"] = 1
                        found_PI_time = Packets[i]["startedDateTime"]
                        found_PI = True

            return VULPIXAnalyzer.score(result_dict), result_dict

        except Exception as err:
            logging.error("Unexpected error during analyze har file.")
            logging.error(err)



if __name__ == '__main__':
    if 2 <= len(sys.argv) <= 3:
        package_name = sys.argv[1]
        pretty = len(sys.argv) == 3 and sys.argv[2] in ['-P', '--prettify']
        score, result = VULPIXAnalyzer.analyze(package_name, PI_file_path="PI.json", har_file=f"../result/{package_name}.har")
        if pretty:            
            print('VULPIX SCORE =', score)
            print()
            for PI in result:
                print('%-60s%-1i   %-12s' % (PI, result[PI], ['Not Found', 'Found'][result[PI]]))
        else:
            print(score, result)
    else:
        print("Usage: ./PI_detection.py <package_name>")
    