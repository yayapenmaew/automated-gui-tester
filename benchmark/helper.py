from bs4 import BeautifulSoup
import logging


class HTMLResultParser:
    def __init__(self, path):
        with open(path, 'r') as fp:
            self.soup = BeautifulSoup(fp.read(), "lxml")

    def detailed_code_cov(self):
        records = self.soup.select('tr')
        result = []
        overall_cov = -1
        for record in records:
            td = record.select('td')
            package = td[0].text.strip()
            try:
                code_cov = float(td[2].text[:-1])
                result.append((package, code_cov))
                if package == "Total":
                    overall_cov = code_cov
            except:
                pass

        return overall_cov, result


if __name__ == '__main__':
    helper = HTMLResultParser('./jococo-example.html')
    print('Code coverage', helper.detailed_code_cov())
