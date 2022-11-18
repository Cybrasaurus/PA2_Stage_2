import json
import copy
from dotenv import dotenv_values


def json_opener(filename):
    with open(f"{filename}.json") as json_file:
        data = json.load(json_file)

    return data


def json_saver(filename, file_contents):
    with open(f"{filename}.json", 'w') as outfile:
        json.dump(file_contents, outfile)


def env_loader_v2():
    env_stuff = dotenv_values("Config/.env")
    usable_dict = dict(env_stuff)
    return usable_dict


def config_cleaning_dict(config_data_to_clean, keyword_dict):
    """
    This function takes the config files which have keywords with company sensitive information, and replaces them
    with the actual keywords
    :param config_data_to_clean: the config data that requires cleaning
    :param keyword_dict: the keyword dictionary
    :return: The cleaned config data
    """
    renamed_column_dict = copy.deepcopy(config_data_to_clean)
    for _ in keyword_dict:
        for items in renamed_column_dict:
            curr_string = renamed_column_dict[items]
            for word, replacement in keyword_dict.items():
                if word in curr_string:
                    renamed_column_dict[items] = curr_string.replace(word, replacement)
                    break
                else:
                    renamed_column_dict[items] = curr_string.replace(word, replacement)
    return renamed_column_dict

def config_cleaning_list(config_data_to_clean, keyword_dict):

    renamed_list = copy.deepcopy(config_data_to_clean)

    for word, replacement in keyword_dict.items():
        for count, items in enumerate(renamed_list):
            if word in items:
                renamed_list[count] = items.replace(word, replacement)

    return renamed_list

def config_cleaner(config_data_to_clean, keyword_dict):
    for keys in config_data_to_clean:
        if isinstance(config_data_to_clean[keys], dict):
            config_data_to_clean[keys] = config_cleaning_dict(config_data_to_clean[keys], keyword_dict)
        elif isinstance(config_data_to_clean[keys], list):
            config_data_to_clean[keys] = config_cleaning_list(config_data_to_clean[keys], keyword_dict)
        elif isinstance(config_data_to_clean[keys], str):
            for word, replacement in keyword_dict.items():
                config_data_to_clean[keys] = config_data_to_clean[keys].replace(word, replacement)

    return config_data_to_clean


if __name__ == "__main__":
    print("Hi")
    json_saver("testing", "Test contents")

    config_contents = json_opener("config")
    print(type(config_contents))
    print(config_contents)
