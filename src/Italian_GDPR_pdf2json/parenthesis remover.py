import re


def remove_text_within_parentheses(text):
    # Regular expression to match everything between parentheses
    pattern = r'\(.*?\)'

    # Substitute all matches with an empty string
    result = re.sub(pattern, '', text)

    return result


# Example usage
text = "(C51) 15) «dati relativi alla salute»: i dati personali attinenti alla salute fisica o mentale di una persona fisica, compresa la prestazione di servizi di assistenza sanitaria, che rivelano informazioni relative al suo stato di salute; (C35) 16) «stabilimento principale»: (C36, C37) a) per quanto riguarda un titolare del trattamento con stabilimenti in più di uno Stato membro, il luogo della sua amministrazione centrale nell'Unione, salvo che le decisioni sulle finalità e i mezzi del trattamento"
cleaned_text = remove_text_within_parentheses(text)

print(cleaned_text)
