from bs4 import BeautifulSoup
import logging

class ACVToolHelper:
    def __init__(self, path):
        with open(path, 'r') as fp:
            self.soup = BeautifulSoup(fp.read(), "lxml")
        self.package_name = self.__get_package_name()
    
    def __get_package_name(self):
        package_name = self.soup.select('li')[0].text.strip()
        logging.info('Extracting code coverage')
        logging.info(f'Package: {package_name}')
        return package_name

    def detailed_code_cov(self):
        records = self.soup.select('tr')
        result = []
        for record in records:
            td = record.select('td')
            package = td[0].text.strip()
            try:
                code_cov = float(td[2].text[:-1])
                result.append((package, code_cov))
            except:
                pass

        return result

    def code_cov(self):
        records = self.soup.select('tr')
        for record in records:
            td = record.select('td')
            package = td[0].text.strip()
            try:
                code_cov = float(td[2].text[:-1])
                if package == self.package_name:
                    return code_cov
            except:
                pass

        return 0


if __name__ == '__main__':
    helper = ACVToolHelper('./example.html')
    print('Code coverage', helper.detailed_code_cov())