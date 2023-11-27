from language import translate_dict


##### TRANSLATIONS #####

def translate(string, language):

    try:
        return translate_dict[string][language]
    except:
        return "Unknown"