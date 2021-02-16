import csv
import os

def clean_csv(filepath_in, filepath_out_folder, filepath_out_name, conf):
    """ takes a csv and creates a new one at
    the specified location. Returns true or false """
    try:
        with open(filepath_in, encoding='utf-8') as f:
            pass
            #print("Directory received")
    except FileNotFoundError:
        print(f"Sorry, the directory {filepath_in} wasn't found.")
        return False

    if conf == 'n':
        # A list of all the columns we want from OpenFace output
        desired_indeces = [1, 8, 9, 290, 291, 292, 293, 294, 295]
        my_index, max_index = 676, 710
        while (my_index < max_index + 1):
            desired_indeces.append(my_index)
            my_index += 1
    elif conf == 'y':
        desired_indeces = [1]

    my_row = []

    # getting the metadata from the filename
    # -1 thorugh -13 is the .jpg.chip.csv
    # age_gender_race_date/time.jpg
    str_i = -14
    age, gender, race, time = None, None, None, None
    meta_info = [time, race, gender, age]
    meta_i = 0
    while meta_i < 4:
        if filepath_in[str_i].isdigit() == False:
            meta_i += 1
            str_i -= 1
            continue
        meta_info[meta_i] = filepath_in[str_i]
        str_i -= 1

    race = int(meta_info[1])
    gender = int(meta_info[2])
            
    # We are copying select columns from the OpenFace file and adding a column that tracks time between blinks
    # As we do this, we will internally track user presence, time spent working, and time on break
    with open(filepath_in) as file_object:                                    # Reading the OpenFace csv file...
        csv_reader = csv.reader(file_object)
        #print("Extracting From File")
        first = True

        with open(os.path.join(filepath_out_folder, filepath_out_name), 'w', newline = '') as new_file:        # ...and writing desired data into a temporary csv file
            csv_writer = csv.writer(new_file)
            
            for line in csv_reader:                     # iterate through each row of the OpenFace file          
                del my_row[:]                          # every pass, we add to this list and write it to the new csv file
                if first:
                    my_row.append("race")
                    my_row.append("gender")
                    first = False
                else:
                    my_row.append(race)
                    my_row.append(gender)

                for index in desired_indeces:           # copying the data from the desired OpenFace columns
                    try:
                        my_row.append(line[index])
                    except IndexError:                  # if a datapoint is missing, it copies a 0
                        my_row.append(0)
            
                csv_writer.writerow(my_row)     # and we write my_row into the new csv file
        
    return True


def find_csv(folder):
    """ Returns a list of absolute filepaths
    for all csv's in a folder """
    csv_list = []
    for filename in os.listdir(folder):
        if filename.endswith(".csv"):
            csv_list.append(os.path.join(folder, filename))
        else:
            continue
    return csv_list


def merge_csv(folder):
    """ merges the output into a single file """
    csv_list = find_csv(folder)
    first = True
    header = True
    my_row = []
    
    try:
        with open(os.path.join(folder, "MERGED.csv"), 'w', newline = '') as new_file:
            csv_writer = csv.writer(new_file)
            
            # for each csv in the folder
            for item in csv_list:
                # open the csv
                with open(item) as file_object:
                    csv_reader = csv.reader(file_object)
                    # if it is the first one, keep the header
                    if first:
                        for line in csv_reader:    
                            del my_row[:]
                            for value in line:
                                my_row.append(value)
                            csv_writer.writerow(my_row)
                        first = False
                    # otherwise, don't keep the header
                    else:
                        header = True
                        for line in csv_reader:    
                            del my_row[:]
                            if header:
                                # the first line
                                header = False
                                continue
                            for value in line:
                                my_row.append(value)
                            csv_writer.writerow(my_row)
    except PermissionError:
        print("ERROR: It looks like MERGED.csv is open, could you close it and try again?")
        return False
    return True


def utk_cleaner(folder, conf):
    """ runs the overall logic """
    # get filepaths of all csv's in folder
    my_list = find_csv(folder)
    print("\nGot list of csv's in directory")

    # create output directory if it doesn't already exist
    destination_name = r'PROCESSED'
    destination_folder = os.path.join(folder, destination_name)
    if not os.path.isdir(destination_folder):
        print("Created a PROCESSED folder in directory")
        os.mkdir(destination_folder)
    else:
        print("PROCESSED folder found in directory")
    
    # process all csv's from list of filepaths
    i = 0
    print("Condensing the csv's...")
    for output in my_list:
        clean_csv(output, destination_folder, 'f'+str(i)+'.csv', conf)
        if i%100 == 0 and i != 0:
            print(f"{i} completed")
        i += 1

    print("\nCsv's have been condensed. Merging.")
    # last function takes all of the csv's in PROCESSED and merges them
    if merge_csv(destination_folder):
        print("Complete! Your file in YourFolder\\PROCESSED\\MERGED.CSV")


if __name__ == "__main__":
    print("\n**************************************************")
    print("Welcome to the OpenFace Cleaner")
    print("It processes csv outputs from OpenFace")
    print("This version is customized for the UTK face dataset")
    print("\nBe sure to close any files in the PROCESSED directory before running!")
    print("\nWhich directory would you like processed?")
    print("(There can be more than csv's in the directory)")
    csv_directory = input("Absolute filepath: ")
    while True:
        conf = input("Would you like just the confidence value? [y][n] ")
        if conf.lower() == 'y' or conf.lower() == 'n': break
        else: print("Invalid input, please try again.")
    utk_cleaner(csv_directory, conf)
    print("**************************************************\n")
