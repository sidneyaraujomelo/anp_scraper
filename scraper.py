from bs4 import BeautifulSoup
import requests
import re

class Glossary():
    def __init__(self):
        self.__dict = {}
    
    def add_entry(self, head: str, definition: str, source: str=""):
        if head in self.__dict:
            print(f"Head {head} already in glossary with definition {self.__dict[head]}")
            print(f"Therefore, we add {definition} under the 'duplicate' key on the glossary")
            self.__dict[head]["duplicates"].append(definition)
            return True
        self.__dict[head] = {"definition": definition, "source": source, "duplicates": []}
        return True

    def __getitem__(self, key):
        if key in self.__dict:
            return self.__dict[key]
        raise KeyError
    
    def get_sources(self):
        sources = [x["source"].replace("\xa0"," ") for x in self.__dict.values()]
        return list(set(sources))
        
def get_soup(url, headers=None):
    req = requests.get(url)
    return BeautifulSoup(req.content, 'html.parser')

def create_glossary(soup):
    all_gloss_letters = soup.select("ul[id^=gloss]")
    glossary = Glossary()
    for gloss_letter in all_gloss_letters:
        for item in gloss_letter.select("li"):
            title = item.find("h3").find("span").text
            text_definition = item.find("p").text
            #print(text_definition)
            # Regex Expression that splits text definition into {definition}, {source}, {alternative definition}
            match = re.match(r"((.+?(?=\(Fonte))(\(Fonte(.+?)\))*)*", text_definition)
            if match is None or match.group(1) is None:
                definition = text_definition
                source = ""
            else:
                # Concatenate definition and alternative definition
                #print(match.groups())
                definition = match.group(2)
                if len(match.groups()) > 2:
                    # Get source and remove '(' and ')'
                    source = match.group(3).replace("(","").replace(")","")
                    if source is None:
                        source = ""
                if len(match.groups()) > 4:
                    definition = definition + match.group(5)
                if len(match.groups()) > 5:
                    source = source + " e " + match.group(6).replace("(","").replace(")","")
                source = source.replace("Fonte","").replace(":","").replace("\xa0"," ").strip()
                #print(title)
                #print(definition)
                #print(source)
            glossary.add_entry(title, definition, source)
    return glossary