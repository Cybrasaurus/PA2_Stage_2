import numpy as np
import pandas as pd
import Cy_Excel as cye
import json
from os.path import exists


# todo print debugging stuff like current headers etc
# todo check hylia requirements for filtering

# TODO date formatting
# todo talk on tufin-ID
# todo talk kfl-projecte go live vs start Date
# TODO rework droplist into drop_columns
# TODO rework add value to column to accept before and after input
#todo rework combine_rows, is combine columns actually
#TODO rework combine_char vs combination_character
#todo drop rows containing
#todo check before concating, all columns same name, whats missing etc

# TODO: add cleaning to dicts and list of keyword operations, make sure they have the right type
# todo rework the env file and all that

def config_validator_individual_file(config_file_name: str):
    """
    This function validates the config files that dictate what is done to the individual Excel files.
    It checks whether proper keys are used and if the values have the correct type
    :param config_file_name: The Name of the Config File
    :return: ---
    """

    # Dict of Allowed Keys + Type
    # TODO maintain this to the current standard of commands
    check_list_individul = {"Excel_Name": "str",
                            "Loader_Variant": "str",
                            "Column_Rename": {},
                            "Drop_List": [],
                            "Reorder_Columns": [],
                            "Split_Row": {},
                            "Export_Progress": "str",
                            "Export_Result": "str",
                            "Replace_Keywords": {},
                            "Replace_Everything": {},
                            "Combine_Rows": {},
                            "Map_Column": {}}

    print(f"config_validator_individual_file --- Starting Validation of {config_file_name}")
    # Check whether the File Exists
    try:
        with open(f"Config/{config_file_name}.json") as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find the config File named '{config_file_name}' in the Config Folder")

    # Check Keys and Types of Values
    for keys in data:
        if keys not in list(check_list_individul.keys()):
            raise KeyError(f"config_validator_individ_file --- Key '{keys}' is not a recognised Key")
        elif not isinstance(data[keys], type(check_list_individul[keys])):
            raise TypeError((
                f"The Value of the Key '{keys}' is a {type(data[keys])}, but it is supposed to be a {type(check_list_individul[keys])}"))
    # Check if the Excel File containing the raw data exists in the Raw Excel File
    if not exists(f"Raw Excel/{data['Excel_Name']}.xlsx"):
        raise FileNotFoundError(f"Could not find the specified Excel File: '{data['Excel_Name']}.xlsx'")

    print(f"config_validator_individual_file --- Successful with {config_file_name}")


def config_validator_main(main_config):
    """
    This function validates the main config files.
    It checks whether proper keys are used and if the values have the correct type
    :param main_config: The Main Config File, a loaded Json in Form of a Dictionary
    :return: ---
    """

    # TODO check if the excel files exist

    # TODO maintain this to the current standard of commands
    check_list_main = {"Files_To_Read": [],
                       "CA_Excel_Column_Order": []}

    print("\nconfig_validator_main --- Running Config Validation")
    print("config_validator_main --- Validating Main Config")
    # Check Keys and Types of Values
    for keys in main_config:
        if keys not in list(check_list_main.keys()):
            raise KeyError(f"Key '{keys}' is not an accepted Keyword ")
        elif not isinstance(main_config[keys], type(check_list_main[keys])):
            raise TypeError((
                f"The Value of the Key '{keys}' is a {type(main_config[keys])}, but it is supposed to be a {type(check_list_main[keys])}"))

    # Check individual Files
    for filenames in main_config['Files_To_Read']:
        config_validator_individual_file(filenames)
    print("config_validator_main --- Successful \n")


def auto_run_config(config_data, main_config):
    # TODO documentation for this
    working_df = ""

    for commands in config_data:
        print(f"Current Operation: {commands['Command']}")
        match commands["Command"]:
            case "Excel_Name":
                working_df = cye.load_excel(f'Raw Excel/{commands["File_Name"]}', commands["Loader_Variant"])
            case "Loader_Variant":
                print("---------")
                continue
            case "Drop_List":
                working_df = working_df.drop(columns=commands["Dropped_Columns"])
            case "Drop_Columns_by_Number":
                working_df = working_df.iloc[:, commands["Drop_From_Left"]:commands["Drop_From_Right"]]
            case "Drop_Rows":
                working_df = working_df.iloc[commands["Drop_From_Top"]:commands["Drop_From_Bottom"], :]
            case "Keep_every_x_Rows":
                working_df = working_df.iloc[::commands["row_skip"]]
            case "Drop_every_x_Rows":
                working_df = working_df.drop(working_df.index[commands["start_row"]::commands["row_skip"]])
            case "Column_Rename":
                working_df.rename(columns=commands["Renaming_Dict"], inplace=True)
            case "Column_Rename_by_List":
                working_df.columns = commands["Renaming_List"]
            case "Reorder_Columns":
                working_df = working_df.reindex(columns=commands["Column_List"])
            # ----------------------------------------------------------------------------
            case "Export_Progress":
                print("The following warning may appear, this is safe to ignore\n##UserWarning: Workbook contains no "
                      "default style, apply openpyxl's default\n##warn('Workbook contains no default style, "
                      "apply openpyxl's default')")
                working_df.to_excel(f"Progress Excels/{commands['File_Name']}.xlsx", index=False)
            case "Export_Result":
                print("The following warning may appear, this is safe to ignore\n##UserWarning: Workbook contains no "
                      "default style, apply openpyxl's default\n##warn('Workbook contains no default style, "
                      "apply openpyxl's default')")
                working_df.to_excel(f"Result Excels/{commands['File_Name']}.xlsx", index=False)
            # ----------------------------------------------------------------------------
            case "Split_Row":
                working_df = cye.generic_row_splitter(input_df=working_df,
                                                      column_to_split=commands["Row_to_Split"],
                                                      split_character=commands["Char_to_Split"])
            # ----------------------------------------------------------------------------
            case "Replace_Keywords":
                working_df[commands["Target_Row"]] = working_df[commands["Target_Row"]].replace(
                    commands["Keyword_Dict"], regex=False)
            case "Replace_Keywords_Entire_Excel":
                working_df = working_df.replace(commands["Keyword_Dict"], regex=False)
            case "Replace_Everything":
                working_df[commands["Target_Row"]] = working_df[commands["Target_Row"]].replace(
                    commands["Keyword_Dict"], regex=True)
            case "Replace_Everything_Entire_Excel":
                working_df = working_df.replace(commands["Keyword_Dict"], regex=True)
            # ----------------------------------------------------------------------------
            case "Map_Column":
                working_df[commands["New_Col_Name"]] = working_df[commands["Source_Col_Name"]].map(
                    commands["Mapping_Values"])
            case "Combine_Rows":
                working_df = cye.generic_column_combiner(input_df=working_df, row_1=commands["First_Row"],
                                                         row_2=commands["Second_Row"],
                                                         row_result=commands["Combined_Row_Name"],
                                                         combine_char=commands["Combine_Character"],
                                                         delete_old=commands["Delete_Source_Rows"])
            case "Combine_Rows_Multiple":
                working_df[commands["Combined_Column_Name"]] = working_df[commands["Combine_List"]].agg(";".join,
                                                                                                        axis=1)
            case "Copy_Column":
                working_df[commands["New_Row_Name"]] = working_df[commands["Source_Row_Name"]]
            case "Isolate_Segment":
                working_df = cye.isolate_segment(working_df, target_row=commands["Target_Row"],
                                                 split_char=commands["Splitting_Character"],
                                                 target_segment=commands["Wanted_Segment"])
            case "Add_Value_to_Column":
                working_df = cye.add_value_to_every_row_in_column(input_df=working_df,
                                                                  target_row_list=commands["Row_List"],
                                                                  added_value_list=commands["Value_List"],
                                                                  combination_char=commands["Combination_Character"])
            case "Drop_Rows_Not_Containing":
                # working_df = working_df[working_df[commands["Target_Column"].str.contains(commands["Keyword"])]]
                working_df = working_df[working_df[commands["Target_Column"]].str.contains(commands["Keyword"]) == True]
            case "Combine_Excels_on_Match":
                working_df = cye.combine_excels_on_match(input_df=working_df,
                                                         aux_excel_name=commands["Auxiliary_Excel_Name"],
                                                         aux_excel_load_variant=commands["Aux_Excel_Loader_Variant"],
                                                         target_column=commands["Target_Column"],
                                                         compared_column=commands["Compared_Column"],
                                                         transferred_column_list=commands["Transferred_Columns"])
            case "Drop_all_NaN":
                working_df = working_df.dropna(how="all")
            case "Purge_empty_rows":
                working_df = working_df.replace("", np.nan)
                working_df = working_df.dropna(axis=0, how="all")
            case "Make_empty_column":
                working_df[commands["New_Col_Name"]] = np.nan
            case "Print_DF":
                print(working_df)
            case "Text_to_Datetime":
                working_df[commands["Target_Column"]] = pd.to_datetime(working_df[commands["Target_Column"]],
                                                                       infer_datetime_format=True)


        working_df = working_df.replace("nan", np.nan)
        working_df = working_df.fillna("")
        #print(working_df)
        print("---Operation Successful---\n")

    # working_df.to_excel("Result Excels/changes_output_autorun.xlsx", index=False)
    return working_df


if __name__ == '__main__':
    pass
