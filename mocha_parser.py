class parser:
    def __init__(self, template, text):
        self.__parameter_data = {}
        
        template_split = template.split("/")
        text_split = text.split("/")

        for x in range(len(template_split)):
            if "{" in template_split[x] and "}" in template_split[x]:
                temp = template_split[x]
                self.__parameter_data[temp[1:-1]] = text_split[x]

    def is_parsable(self):
        if not self.__parameter_data:
            return False
        return True

    def parse(self):
        return self.__parameter_data