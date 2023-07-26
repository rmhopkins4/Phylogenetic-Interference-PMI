import json


class Language:
    """
    This class represents a language.

    State:
    - `name (str)`: name of the language. Ex: "STANDARD_GERMAN"
    - `word_list (list[list[str]])`: list of concepts' words. Is a list of lists because some concepts have multiple words in the same language.

    Both name and word_list are public.

    Constructor:
    - `name: str`
    - `word_list: list[list[str]]`

    Pretty self-explanatory

    Methods:
    - `__str__(self)`: Returns a string representation of the Language object.

    Example:
    ```py
    # Create instances of Language
    language1 = Language("English", [["hello", "world"], ["apple", "banana"]])
    language2 = Language("French", [["bonjour", "monde"], ["pomme", "banane"]])
    language3 = Language("German", [["hallo", "welt"], ["apfel", "banane"]])

    # List of Language objects
    languages_list = [language1, language2, language3]

    # Print the Language objects
    for language in languages_list:
        print("Name:", language.name)
        print("Word List:", language.word_list)
        print("---")
    ```
    """

    def __init__(self, name: str, word_list: list[list[str]]) -> None:
        self.name = name
        self.word_list = word_list

    def __str__(self):
        return f"{self.name}: {self.word_list}"
