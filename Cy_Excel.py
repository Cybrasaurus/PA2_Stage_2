import copy
import warnings
from openpyxl.utils import column_index_from_string as opyxl_get_column_index
import pandas as pd


# TODO check $$ marks for other todos


def get_pd_df_column_index(ExcelColumn: str):
    """[This function takes an Excel Column Name and returns the corresponding pandas dataframe column index.
        Note that the openpyxl.utils column_index_from_string Function return the index '1' for the Excel Column 'A',
        whereas the first column in a pandas dataframe is '0']

    Args:
        ExcelColumn (str): [The Column Name in the Excel, e.g. 'D', 'AB']

    Returns:
        [int]: [The equivalent Column Index in the Pandas Dataframe]
    """
    if type(ExcelColumn) == str:
        is_letter = False
        for characters in ExcelColumn:

            if characters.isalpha:
                is_letter = True
            elif is_letter == False:
                print("Cy_Excel -- get_pd_df_column_index:", characters, "in", ExcelColumn,
                      "is not a Valid Character, needs to be a Letter of the Alphabet")
                break

        if is_letter != False:
            try:
                Col_Int = opyxl_get_column_index(ExcelColumn)
                # deduct 1 to convert from from openpyxl to pandas DF equivalent column
                Col_Int -= 1
                return Col_Int
            except ValueError as VE:
                print(VE)
    else:
        raise Exception(
            "Cy_Excel -- get_pd_df_column_index: Input Parameter is invalid, needs to be a string but is a ",
            type(ExcelColumn))


def get_excel_select_rowsAndColumns(df_to_modify, selected_rows: list, selected_columns: list):
    """[summary]$$ todo docu

    Args:
        df_to_modify ([type]): [description]
        selected_rows (list): [description]
        selected_columns (list): [description]

    Returns:
        [type]: [description]
    """

    for elements in range(len(selected_columns)):
        selected_columns[elements] = get_pd_df_column_index(selected_columns[elements])

    try:
        df_to_modify = df_to_modify.iloc[selected_rows, selected_columns]
        return df_to_modify
    except IndexError:
        print(
            "Cy_Excel -- get_excel_to_df_segment: Selected Rows are out of bounds, please selected a range of cells that contain values")


def get_excel_range(df_to_modify, start_row: int = None, end_row: int = None, start_col: int = None,
                    end_col: int = None):
    # $$documentation
    if start_row != None and start_row <= 0:
        raise Exception("The Starting Row may not be smaller than 0 \n Cy-Excel Module, get_excel_range() Function")
    if start_col != None:
        start_col = get_pd_df_column_index(start_col)
    if type(end_col) == str:
        end_col = get_pd_df_column_index(end_col) + 1
    elif type(end_col) == int and end_col <= 0:
        end_col = end_col

    if start_row != None and start_row >= 0:
        start_row -= 1
    # $$implement config file blank handling here
    df_to_modify = df_to_modify.iloc[start_row:end_row, start_col:end_col]
    return df_to_modify


def load_excel(excel_file_name: str, loader_variant: str):
    """
    Basic Function to load Excel files and return them as a pandas dataframe
    The Column Headers ore enumerated, starting from 0, or keep the excel first row
    Args:
        excel_file_name: The Name of the Source Excel

    Returns: A Pandas dataframe

    """
    if loader_variant == "Numeric_Headers":
        return pd.read_excel(f'{excel_file_name}.xlsx', header=None)
    elif loader_variant == "Excel_Headers":
        return pd.read_excel(f'{excel_file_name}.xlsx')
    else:
        raise Exception("Cy_Excel: load_excel encountered an invalid loading Variant")


def generic_row_splitter(input_df, column_to_split: str, split_character: str):
    """
    This function splits a row containing multiple data into multiple, separate rows. Here's an alternate solution to the same problem: https://sureshssarda.medium.com/pandas-splitting-exploding-a-column-into-multiple-rows-b1b1d59ea12e
    :param input_df: The Pandas DF that contains data with multiples
    :param column_to_split: The Pandas Column Name containing rows with multiples
    :param split_character: The Character (or String) identifying the splitting operation
    :return: The Dataframe with more rows
    """
    splitting_dict = input_df.to_dict(orient="list")

    key_list = list(splitting_dict.keys())
    keylist_2 = copy.deepcopy(key_list)

    try:
        keylist_2.remove(column_to_split)
    except ValueError as ve:
        print(f"Got Value Error: {ve}")
        print(f"The Column Name does not exist in the Dataframe. Here is a list of all column names: \n"
              f"{key_list}\n Trying to remove: {column_to_split}")

    output_records = {}
    for items in key_list:
        output_records[items] = []

    for curr_iteration, keys in enumerate(splitting_dict[column_to_split]):
        try:
            temp_var = keys.split(split_character)
        except AttributeError:
            keys = str(keys)
            temp_var = keys.split(split_character)

        for entries in temp_var:
            output_records[column_to_split].append(entries.strip())  # strip() to remove trailing & leading whitespaces
            for items in keylist_2:
                output_records[items].append(splitting_dict[items][curr_iteration])

    return_df = pd.DataFrame.from_dict(output_records)
    return return_df


def generic_column_combiner(input_df, row_1: str, row_2: str, row_result: str, combine_char: str,
                            delete_old: str = "True"):
    # TODO Documentation
    if delete_old == "True":
        # create temporary copy of result so the old columns can be deleted, even if the new combined column has the
        # same name as one of the old rows
        temp_df = input_df[row_1].astype(str) + str(combine_char) + input_df[row_2].astype(str)
        input_df = input_df.drop(columns=[row_1, row_2])
        input_df[row_result] = temp_df
    else:
        input_df[row_result] = input_df[row_1].astype(str) + str(combine_char) + input_df[row_2].astype(str)
    return input_df

def isolate_segment(input_df, target_row, split_char, target_segment):
    splitting_dict = input_df.to_dict(orient="list")
    # TODO docu
    for count, items in enumerate(splitting_dict[target_row]):
        try:
            current_list = items.split(split_char)
        except AttributeError:
            items = str(items)
            current_list = items.split(split_char)

        try:
            splitting_dict[target_row][count] = current_list[target_segment].strip()
        except IndexError:
            splitting_dict[target_row][count] = current_list[len(current_list)-1].strip()


    return_df = pd.DataFrame.from_dict(splitting_dict)
    return return_df


def add_value_to_every_row_in_column(input_df, target_row_list, added_value_list,combination_char):
    # TODO docu
    splitting_dict = input_df.to_dict(orient="list")
    modifing_dict = copy.deepcopy(splitting_dict)

    # rows = DE, FR, BE...
    for rows, added_value in zip(target_row_list, added_value_list):
        # splitting_dict[rows] = [entry1, entry2, entry3...]
        # items = entry1, entry2, entry3...
        for count,items in enumerate(splitting_dict[rows]):
            modifing_dict[rows][count] = f"{added_value}{combination_char}{items}"

    return_df = pd.DataFrame.from_dict(modifing_dict)
    return return_df


def combine_excels_on_match(input_df, aux_excel_name, aux_excel_load_variant, target_column, compared_column,
                            transferred_column_list):

    aux_excel = load_excel(excel_file_name=aux_excel_name, loader_variant=aux_excel_load_variant)

    splitting_dict = input_df.to_dict(orient="list")
    modifying_dict = copy.deepcopy(splitting_dict)
    aux_dict = aux_excel.to_dict(orient="list")



    for new_columns in transferred_column_list:
        modifying_dict[new_columns]=[]
        for times in range(len(splitting_dict[target_column])):
            modifying_dict[new_columns].append("")

    # items = entry1, entry2...
    for primary_count, items in enumerate(splitting_dict[target_column]):
        # potential_matches = potent1, potent2...
        for count, potential_matches in enumerate(aux_dict[compared_column]):
            if str(items) in str(potential_matches):
                for transfers in transferred_column_list:
                    modifying_dict[transfers][primary_count] = (aux_dict[transfers][count])

    return_df = pd.DataFrame.from_dict(modifying_dict)
    return return_df

if __name__ == '__main__':
    # print(get_excel_select_rowsAndColumns(df,rowlist, collist))
    df = load_excel("Tester")
    print(get_excel_range(df, start_row=2, end_row=10, start_col="C", end_col="H"))
