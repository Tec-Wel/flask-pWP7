"""
A simple content-based recommender system that recommends Welfie resources to users based on their preferences.
"""

import pandas as pd 
import sys 
import utils
from flask import Flask, request, jsonify, abort, current_app
from flask_cors import CORS

app = Flask(__name__)
app.config['CORS_HEADER'] = 'Content-Type'
CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)








@app.route('/recommend', methods=['POST'])
def process_data():
        # Read user and movie data from CSV files
        user_csv = pd.read_csv('Welfie_Users.csv')
        resources_csv = pd.read_csv('Mental_Health_Resources.csv')

        # Each user has keys: 'Name', ...
        users_dict = user_csv.to_dict('records')

        # User -> Resource 
        # Age -> Target Audience (Done)
        # Geographic Focus -> Geographic Focus (Done)
        # MHQ Score -> Welfie Rating (0-19 = 1, 20-39 = 2, 40-59 = 3, 60-79 = 4, 80-100 = 5) (Done)
        # LGBTQ+ Friendly -> LGBTQ+ Friendly (Done)
        # Technical Proficiency -> Tech. Equity (1=Low, 4=High) (Done)
        # Type of Organization -> Type of Organization (Done)
        # 
        # Other Preferences -> Pros, Cons, 

        # user_attributes_that_is_a_list = ["Health Service Providers", "Type of Medicine", "Commonly Used Language*", "Clinical Diagnosis (DSM-V)", "Other Preferences"]
        user_attribute_list = ["Name", "Age", "LGBTQ+ Friendly", "MHQ score", "Geographic Focus", "Technical Proficiency", 
                            "Type of Organization"]
        users = {}
        for user in users_dict: 
            attribute_dict = {}
            for k in user.keys():
                if k in user_attribute_list:
                    # attribute_dict[k] = user[k]
                    attribute_dict[k] = [x.strip() for x in str(user[k]).split(',')]
                # elif k != 'User ID':
                    # attribute_dict[k] = user[k]
            users[str(user['User ID'])] = attribute_dict


        resources_dict = resources_csv.to_dict('records')

        # resource_attributes_that_is_a_list = ["Medium(s)", "Social Media", "Target Community", "Target Audience", "Commonly Used Language", "Clinical Diagnosis (DSM-V)", "Pros", "Cons", "When to Use", "Health Service Providers", "Type of Medicine", "Approvals", "Covered By"]
        # resource_attribute_list = ["Target Audience", "Geographic Focus", "LGBTQ+ Friendly"]
        resource_attribute_list = ["Target Audience", "LGBTQ+ Friendly", "Welfie Rating", "Geographic Focus", "Tech. Equity",
                                "Type of Organization"]
        resources = {}
        for resource in resources_dict:
            attribute_dict = {}
            for k in resource.keys():
                # if pd.isna(resource[k]):
                #     attribute_dict[k] = None
                if k in resource_attribute_list:
                    attribute_dict[k] = [x.strip() for x in str(resource[k]).split(',')]
                # elif k != 'Name':
                    # attribute_dict[k] = resource[k]
            resources[resource["Name"]] = attribute_dict

        utils.print_dict(1, users, "User Dictionary: ")
        utils.print_dict(1, resources, "Resource Dictionary: ")

        age_map = {"Young Adult: 17-21": (17,21), 
                            "Adult: 21+": (21,150), 
                            "Highschool: 9-12": (14,19), 
                            "K-12": (3,19), 
                            "Middle: 7-8": (11,14), 
                            "Elementary: 1-5": (4,9)}

        # 0-19 = 1, 20-39 = 2, 40-59 = 3, 60-79 = 4, 80-100 = 5
        mhq_map = {"1.0": (0, 19), 
                            "2.0": (20, 39),
                            "3.0": (40, 59),
                            "4.0": (60, 79),
                            "5.0": (80, 100)}
        


        def recommend(resources: dict, query_userID: str) -> tuple[list, dict]: 
            final_resources_rank = {}
            recommended_list = [] # i.e. all attributes match 
            num_attributes = 3
            resources_list = []

            for resource, attribute in resources.items():
                count_satisfied = 0
                # only suggest resource if +/- x away from user's preference
                can_suggest = True
                # 1) Age -> Target Audience
                for audience in attribute['Target Audience']:
                    if audience == 'nan': 
                        continue
                    # print(audience, type(audience)) 
                    if age_map[audience][0] <= int(users[query_userID]['Age'][0]) <= age_map[audience][1]:
                        count_satisfied += 1
                        break
                # 2) LGBTQ+ Friendly -> LGBTQ+ Friendly
                lgbt_off = abs(float(attribute['LGBTQ+ Friendly'][0]) - float(users[query_userID]['LGBTQ+ Friendly'][0]))
                if lgbt_off == 0:
                    count_satisfied += 1
                if lgbt_off > 1:
                    can_suggest == False
                
                # 3) MHQ Score -> Welfie Rating (0-19 = 1, 20-39 = 2, 40-59 = 3, 60-79 = 4, 80-100 = 5)
                rating = attribute['Welfie Rating'][0]
                if rating != 'nan':
                    if mhq_map[rating][0] <= int(users[query_userID]['MHQ score'][0]) <= mhq_map[rating][1]:
                        count_satisfied += 1
                
                # 4) Geographic Focus -> Geographic Focus
                if users[query_userID]['Geographic Focus'][0] == 'NONE':
                    count_satisfied += 1
                else:
                    if attribute['Geographic Focus'][0] != 'nan':
                        if attribute['Geographic Focus'][0] == users[query_userID]['Geographic Focus'][0]:
                            count_satisfied += 1

                # 5) Technical Proficiency -> Tech. Equity (1=Low, 4=High) 
                # TODO: only suggest resource if +/- x away from user's preference
                tech_off = abs(float(attribute['Tech. Equity'][0]) - float(users[query_userID]['Technical Proficiency'][0]))
                if tech_off == 0:
                    count_satisfied += 1
                if tech_off > 1:
                    can_suggest == False

                # 6) Type of Organization -> Type of Organization
                if attribute['Type of Organization'][0] != 'nan':
                    if attribute['Type of Organization'][0] == users[query_userID]['Type of Organization'][0]:
                        count_satisfied += 1

                # Add resource to recommended_list if all attributes are satisfied
                resource_row = f"""Name: {resource}, #Satisfied Attribute: {count_satisfied}, 
                                Target Audience: {attribute['Target Audience']}, 
                                LGBTQ+ Friendly: {attribute['LGBTQ+ Friendly'][0]},
                                Welfie Rating: {rating}, 
                                Geographic Focus: {attribute['Geographic Focus'][0]}, 
                                Tech. Equity: {attribute['Tech. Equity'][0]},
                                Type of Organization: {attribute['Type of Organization'][0]}"""
                
                # resource_object = {
                #     "name" : resource,
                #     "url" : attribute['URL'],
                #     "picture" : attribute['Photo'] 
                # }


                if count_satisfied == num_attributes:
                    recommended_list.append(resource_row)
                    for res in resources_dict:
                        if res['Name'] == resource:
                            resource_object = {
                                "name" : res['Name'],
                                "url" : res['URL'],
                                "Photo" : res['Photo']
                            }
                            resources_list.append(resource_object)
                            print(resources_list)
                                
                else:
                    if not can_suggest:
                        continue
                    # record ranking of suggested recommendations
                    if count_satisfied not in final_resources_rank:
                        final_resources_rank[count_satisfied] = [resource_row]
                    else:
                        final_resources_rank[count_satisfied].append(resource_row)

            
            return recommended_list, final_resources_rank, resources_list
        data = request.get_json()
        print(data)
        index = str(data['index'])
        print(users.keys())
        resources_list = []

        if index not in users.keys():
            print(f"User ID ({index}, type:{type(index)}) not in database")
            exit()
        else: 
            print("\nUser Preferences: ", users[index], "\n")
            all_satisfied, final_resources_rank, resources_list = recommend(resources, index) 
            utils.print_list(all_satisfied, "Recommended Resources:")
            num_suggested = 3
            count = 0
            suggested = []
            for i in sorted(final_resources_rank.keys(), reverse=True):
                for j in final_resources_rank[i]:
                    suggested.append(j)
                    count += 1
                    if count >= num_suggested:
                        break
                if count >= num_suggested:
                    break
            utils.print_list(suggested, "Suggested Resources: ")
        print(resources_list)

        return jsonify(resources_list)



@app.route('/', methods=['GET'])
def server_status():
    return "Server is running"




if __name__ == '__main__':    
    app.run(host='0.0.0.0', port=5000)
