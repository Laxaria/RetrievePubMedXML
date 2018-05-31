import lxml.etree
# import pandas as pd
import json
import urllib.parse
import urllib.request
import time

# Establish config parameters
PubMed_eUtil_url_POST = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/epost.fcgi"
PubMed_eUtil_url_FETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
PubMed_database = "pubmed"
WebEnv = ""
Query_Key = ""
PMID_List = []

# Import PMID List
def PMID_List_Import():
    try:
        with open("PMID List.txt", "r") as PMIDList:
            for line in PMIDList:
                try:
                    line = int(line.strip('\n'))
                    PMID_List.append(line)
                except ValueError:
                    pass
    except IOError:
        print("Missing PMID List.txt file")

# Create or load config file storing API keys and other identifying information
def Config_File():
    try:
        with open("config.json") as config_file:
            config_data = json.load(config_file)
    except IOError:
        with open("config.json", "w") as config_file:
            input_APIKey = input("What is your API Key? ")
            input_EMail = input("What is your email address? ")
            input_ToolDesc = input("Describe this tool. ").strip()
            dict_config = { "APIKey": input_APIKey, \
                            "Email": input_EMail, \
                            "Tool Description": input_ToolDesc}
            config_file.write(json.dumps(dict_config))
    return config_data

# Post list of PMIDs to Eutrez History Server
# Return WebEnvironment and Query Key for EFetch
def Post_PMID_To_History_Server(config):
    PMID_List_Count = [str(entry) for entry in PMID_List]
    HTTP_Post_Data = {"db": PubMed_database, \
                      "tool": config["Tool Description"].strip(), \
                      "email": config["Email"].strip(), \
                      "api_key": config["APIKey"].strip(), \
                      "id": ",".join(PMID_List_Count).strip()}
    data = urllib.parse.urlencode(HTTP_Post_Data)
    data = data.encode('utf-8')
    req = urllib.request.Request(PubMed_eUtil_url_POST, data)
    with urllib.request.urlopen(req) as response:
        root = lxml.etree.parse(response)
        WebEnv = root.find('WebEnv').text
        Query_Key = root.find('QueryKey').text
    return [WebEnv, Query_Key]
    
# Query EFetch for full entry information
def Fetch_Entries_From_Server(config, WE,QK):
    Number_Of_Retrievals = 10
    HTTP_Post_Data = {"db": PubMed_database, \
                      "tool": config["Tool Description"].strip(), \
                      "email": config["Email"].strip(), \
                      "api_key": config["APIKey"].strip(), \
                      "WebEnv": WE, \
                      "query_key":  QK, \
                      "retmode": "xml", \
                      "retmax": Number_Of_Retrievals}
    data = urllib.parse.urlencode(HTTP_Post_Data)
    data = data.encode('utf-8')
    req = urllib.request.Request(PubMed_eUtil_url_FETCH, data)
    with urllib.request.urlopen(req) as response:
        returnedXML = lxml.etree.parse(response)
        with open("fetched data.xml", "w") as fetched_data:
            fetched_data.write(lxml.etree.tostring(returnedXML).decode('utf-8'))

def main():
    PMID_List_Import()
    print("Importing PMID List from PMD List.txt")
    time.sleep(1)
    config = Config_File()
    print("Importing config information from config.json")
    time.sleep(1)
    History_Server_Info = Post_PMID_To_History_Server(config)
    print("Posting PMIDs to EUtilz History Server")
    print("WebEnv: {}\nQuery_Key: {}".format(History_Server_Info[0],History_Server_Info[1]))
    time.sleep(1)
    Fetch_Entries_From_Server(config,History_Server_Info[0],History_Server_Info[1])
    print("Successfully wrote to fetched data.xml")

main()


