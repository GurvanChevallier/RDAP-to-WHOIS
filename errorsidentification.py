import json
import vcard
from tqdm import tqdm
from pprint import pprint
with open("amsterdam.txt", "r") as samplefile:
    vcardArrayformatviolation = 0
    entitycount = 0
    for content in tqdm(samplefile, total=206):
        jsonsamples = json.loads(content)
        if "200" not in jsonsamples["status_code"] or jsonsamples["status_code"] == "Cannot read the body":
            continue
        RDAPresponse = json.loads(jsonsamples.get("val"))
        if "entities" in RDAPresponse:
            for entity in RDAPresponse.get("entities"):
                entitycount += 1
                if entity.get("vcardArray")[0] == "vcard": # Section 3.2 of the
                    #pprint(vcard.extract_info_from_vcard(entity.get("vcardArray")[1]))
                    for vCards in entity.get("vcardArray")[1]:
                        pprint(vCards)
                else:
                    vcardArrayformatviolation += 1
    print("Violation of the vcard data structure: "+ str(vcardArrayformatviolation) + " out of " + str(entitycount) )