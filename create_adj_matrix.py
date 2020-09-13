import pandas as pd
import csv
import numpy as np
import scipy.linalg as linalg

def main():
    year = 2010
    data_file = './data/oil_27/processed_data_' + str(year) +  '_27.csv'
    
    import_export_dic, id_to_matrixid, matrixid_to_id, \
    country_codes_withdata, id_to_country_dic, country_to_iso = preprocess_year(data_file)

    matrix = create_adjacency_matrix(import_export_dic, id_to_matrixid,
                                     matrixid_to_id, len(country_codes_withdata))

    print(matrix)
    print(matrix.shape)
    

def create_adjacency_matrix(impexp_dic, id_to_matrixid, matrixid_to_id, n):
    """creates a Hermitian adjacency matrix for the UN GlobalCom_data"""

    adj_matrix = np.zeros((n,n))

    # compute trade difference
    for element in impexp_dic:
        country1_id = id_to_matrixid[element[0]]
        country2_id = id_to_matrixid[element[1]]

        export_1_to_2 = impexp_dic[(element[0], element[1])][1]
        export_2_to_1 = impexp_dic[(element[1], element[0])][1]

        difference = export_1_to_2 - export_2_to_1

        adj_matrix[country1_id, country2_id] = difference

    return adj_matrix*(adj_matrix > 0)

def preprocess_year(data_file):
    
    # list of country names
    countries = []
    # list of country idx
    countries_idx = []
    # create hash maps for countries to id
    id_to_country_dic = {}
    country_to_id_dic = {}
    # create list for all countries involved in trade for specific commodity
    country_codes_withdata = []

    # dictionary mapping country codes to indices in adjacency matrix
    id_to_matrixid = {}
    matrixid_to_id = {}

    # we need to create a list of all country codes that have data available to create a denser
    # adjacency matrix
    country_to_iso = {}
    iso_to_country = {}
    import_export_dic = {}
    country_world_imp_dic = {}
    country_world_exp_dic = {}
    reporters = []
    partners = []

    with open(data_file, mode='r') as clean_file:
        reader = csv.DictReader(clean_file)

        # we read some of the data from the csv file
        for row in reader:
            reporter = row['Reporter']        
            reporter_id = int(row['Reporter Code'])
            reporter_ISO = row['Reporter ISO']

            partner = row['Partner']
            partner_id = int(row['Partner Code'])
            partner_ISO = row['Partner ISO']

            trade_flow_code = int(row['Trade Flow Code'])
            money = int(row['Trade Value (US$)'])

            # partner_id 0 is the world, so get some information of world trade data
            # for each country
            if partner_id == 0:
                if trade_flow_code == 1:
                    country_world_imp_dic[reporter_id] = money
                if trade_flow_code == 2:
                    country_world_exp_dic[reporter_id] = money

            # an id of 0 corresponds to trade to rest of world. Not relevant for adj matrix
            if not(reporter_id == 0 or partner_id == 0):

                if reporter_id not in country_codes_withdata:
                    country_codes_withdata.append(reporter_id)

                if partner_id not in country_codes_withdata:
                    country_codes_withdata.append(partner_id)


                if reporter_id not in reporters:
                    reporters.append(reporter_id)
                if partner_id not in partners:
                    partners.append(partner_id)

                # we create our dictionaries 
                country_to_iso[reporter] = reporter_ISO
                country_to_iso[partner] = partner_ISO

                iso_to_country[reporter_ISO] = reporter
                iso_to_country[partner_ISO] = partner

                country_to_id_dic[partner] = int(partner_id)
                country_to_id_dic[reporter] = int(reporter_id)

                id_to_country_dic[int(partner_id)] = partner
                id_to_country_dic[int(reporter_id)] = reporter

    # we number the country codes from 1 to n, so we can use these new indices
    # for the adjacency matrix
    for i, ids in enumerate(country_codes_withdata):
        id_to_matrixid[ids] = i
        matrixid_to_id[i] = ids

    # dictionary that notes import and export value between each pair of countries,
    # for each reporting country. import is first value, export is second value
    for i in country_codes_withdata:
        for m in country_codes_withdata:
            import_export_dic[(i, m)] = [0,0]

    # plug in values for all the import and export countries
    with open(data_file, mode='r') as clean_file:
        reader = csv.DictReader(clean_file)

        for row in reader:
            reporter_id = int(row['Reporter Code'])
            partner_id = int(row['Partner Code'])
            trade_flow_code = int(row['Trade Flow Code'])
            money = int(row['Trade Value (US$)'])

            reporter_ISO = row['Reporter ISO']
            partner_ISO = row['Partner ISO']


            if not (reporter_id==0 or partner_id==0):
                # import is the first index, export is second
                if trade_flow_code == 1:
                    import_export_dic[(reporter_id, partner_id)][0] = money
                if trade_flow_code == 2:
                    import_export_dic[(reporter_id, partner_id)][1] = money


    # if countries report different trade values (as reporting and partner countries with each other,
    # we take the average of both values. If only one of them reports value we take that one.
    for pair in import_export_dic:
        original = import_export_dic[(pair[0], pair[1])]
        reverse = import_export_dic[(pair[1], pair[0])]

        # initialise variables
        new_original = [0,0]
        new_reverse = [0,0]

        # compare import and expo
        if original[0] != 0 and reverse[1] != 0:
            average = (original[0] + reverse[1])/2
            new_original[0] = average
            new_reverse[1] = average
        elif original[0] != 0 and reverse[1] == 0:
            value = original[0]
            new_original[0] = value
            new_reverse[1] = value
        elif original[0] == 0 and reverse[1] != 0:
            value = reverse[1]
            new_original[0] = value
            new_reverse[1] = value
        else:
            if not pair[0] == pair[1]:
                # add a little bit of noise so matrix won't be non-singular
                value = np.random.rand()
                new_original[0] = value
                new_reverse[1] = value

        # other way around
        if original[1] != 0 and reverse[0] != 0:
            average = (original[1] + reverse[0])/2
            new_original[1] = average
            new_reverse[0] = average
        elif original[1] != 0 and reverse[0] == 0:
            value = original[1]
            new_original[1] = value
            new_reverse[0] = value
        elif original[1] == 0 and reverse[0] != 0:
            value = reverse[0]
            new_original[1] = value
            new_reverse[0] = value
        else:
            if not pair[0] == pair[1]:
                value = np.random.rand()
                new_original[1] = value
                new_reverse[0] = value

        import_export_dic[(pair[0], pair[1])] = new_original
        import_export_dic[(pair[1], pair[0])] = new_reverse

    sum_total_export_dic = {}
    sum_total_import_dic = {}

    # get total trade after adding random noise to data
    for i in country_codes_withdata:
        sum_total_export_dic[i] = 0
        sum_total_import_dic[i] = 0

    for pair in import_export_dic:
        sum_total_export_dic[pair[0]] += import_export_dic[pair][1]
        sum_total_import_dic[pair[0]] += import_export_dic[pair][0]

    return import_export_dic, id_to_matrixid, matrixid_to_id, country_codes_withdata, id_to_country_dic, country_to_iso

if __name__ == "__main__":
    main()
