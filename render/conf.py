from ConfigParser import * 

'''
Usage:
Call ConfParser to parse you *.conf files. 
EX: ConfParser("File.Conf")

Getting a value is done by stating it's section and then the value you want.
EX: parsedContent = ConfParser("File.Conf")
    print parsedContent("section", "value")

Class also contains method to write sections, and values
'''

class ConfParser:

    def __init__(self, fileLocation="xmlConvert.conf"):
        self.config = ConfigParser()
        self.config.read(fileLocation)
        self.fileLocation = fileLocation
    
    def get_value(self, section, option):
        try:
            return self.config.get(section, option)
        except NoSectionError, e:
            print e
        except NoOptionError, e:
            print e 
    
    def __call__(self, section, option):
        try:
            return self.config.get(section, option)
        except NoSectionError, e:
            print e
        except NoOptionError, e:
            print e
    
    def printAllValues(self):
        for section in self.config.sections():
            print section
            for option in self.config.options(section):
                print "	", option ,"=", self.config.get(section, option)
 
    def addSection(self, section):
        try:
            self.config.add_section(section)
        except DuplicateSectionError, e:
            print e
        self.config.write(open(self.fileLocation, "w"))

    def addOption(self, section, option, content):
        try:
            self.config.set(section, option, content)
        except NoSectionError, e:
            print e
        self.config.write(open(self.fileLocation, "w"))
    
    def removeSection(self, section):
        try:
            self.config.remove_section(section)
        except NoSectionError, e:
            print e
        self.config.write(open(self.fileLocation, "w"))
    
    def removeOption(self, section, option, content):
        try:
            self.config.remove_option(section, option)
        except NoSectionError, e:
            print e
        self.config.write(open(self.fileLocation, "w"))

#MAIN STUFF
if __name__ == '__main__':
    conf = ConfParser()
    conf.printAllValues()
