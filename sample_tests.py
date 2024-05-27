import vcard
import main
import json
from pprint import pprint

def sample_processing():
    with open("/home/gurvanc/Documents/data/RDAP_sample.json", "r") as samplefile:
        errors = {}
        unrecognized = {}
        for i in range(0,int(nbsamples)):
            sample_json = json.loads(samplefile.readline())
            ## rejecting the cases where analysis of the RDAP response will be useless/impossible ##
            if sample_json.get("mode") != "rdap":
                print("INFO: Sample with a mode not fitting (!=rdap), skipping")
                continue
            if sample_json.get("status_code")[0] != "200":
                print("INFO: Sample with a status code not fitting (!=200), skipping")
                continue
            if sample_json.get("val") == "Cannot read the body":
                print("INFO: Sample with RDAP response body not readable, skipping")
                continue

            lookup_sample = json.loads(sample_json.get("val"))
            #pprint(lookup_sample)
            #print("\n\n")
            for entity in lookup_sample.get("entities"):
                vcardArray = entity.get("vcardArray")
                if vcardArray is None:
                    print("ERROR: vcardArray empty")
                else:
                    if vcardArray[0] == "vcard":
                        #print(vcardArray[1])
                        infos = vcard.extract_info_from_vcard(vcardArray[1])
                        if infos.get("error") is not None:
                            errors[infos.get("error")] += 1
                        if infos.get("unrecognized"):
                            for elt in infos.get("unrecognized"):
                                if elt not in unrecognized:
                                    unrecognized[elt]= 1
                                else:
                                    unrecognized[elt] += 1
        print("vcards with unrecognized properties:\n")
        pprint(unrecognized)
        print("Error type count:\n")
        pprint(errors)

nbsamples = input("RDAP-to-WHOIS | Enter number of samples to test ")
sample_processing()