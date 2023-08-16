import xml.etree.ElementTree as ET
import json


def main():
    # Define the namespace
    namespace = {'cwe': 'http://cwe.mitre.org/cwe-6'}

    # Parse the XML data
    tree = ET.parse('cwec_v4.10.xml')
    root = tree.getroot()

    # Extract the weakness information into a dictionary
    weakness_dict = {"-1": "Unclassified Vulnerability"}
    for weakness in root.findall('.//cwe:Weakness', namespace):
        weakness_dict[weakness.attrib['ID']] = weakness.attrib['Name']

    for category in root.findall('.//cwe:Category', namespace):
        cwe_ids = find_cwe_ids(namespace, category)
        for cwe_id in cwe_ids:
            weakness_dict[cwe_id] = category.attrib['Name']

    # Write the dictionary to a JSON file
    with open('cwe_names.json', 'w') as f:
        json.dump(weakness_dict, f, indent=4)

    print('JSON data written to cwe_names.json')


def find_cwe_ids(namespace, category):
    cwe_ids = [category.attrib['ID']]
    for member in category.findall('.//cwe:Has_Member', namespace):
        cwe_ids.append(member.attrib['CWE_ID'])
    return cwe_ids


if __name__ == '__main__':
    main()
