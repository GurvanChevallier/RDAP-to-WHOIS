from pprint import pprint
from tqdm import tqdm
import vcard
import csv
import tldextract
import json
import os
import sys

f = open(os.devnull, "w")
sys.stdout = f


def display_whois_data(whois_data):
    unrecognized = {}
    errors = {}
    printed = {}
    if whois_data.get("domain_name"):
        print("Domain Name: " + whois_data.get("domain_name"))
        if "domain_name" not in printed:
            printed["domain_name"] = 1
    if whois_data.get("registry_domain_id"):
        print("Registry Domain ID: " + whois_data.get("registry_domain_id"))
        if "registry_domain_id" not in printed:
            printed["registry_domain_id"] = 1
    if whois_data.get("registrar_rdap_server"):
        print("Registrant RDAP Server: " + whois_data.get("registrar_rdap_server"))
        if "registrar_rdap_server" not in printed:
            printed["registrar_rdap_server"] = 1
    if whois_data.get("lastChangedDate"):
        print("Updated Date : " + whois_data.get("lastChangedDate"))
        if "updatedDate" not in printed:
            printed["updatedDate"] = 1
    if whois_data.get("creationDate"):
        print("Creation Date : " + whois_data.get("creationDate"))
        if "creationDate" not in printed:
            printed["creationDate"] = 1
    if whois_data.get("expirationDate"):
        print("Registrar Registration Exipration Date : " + whois_data.get("expirationDate"))
        if "expirationDate" not in printed:
            printed["expirationDate"] = 1
    # pprint()
    if whois_data.get("entities"):
        for entity in whois_data.get("entities"):
            for role in entity:
                for vcard_elem in entity.get(role):
                    if role == "registrar":
                        match vcard_elem:
                            case "fn":
                                print(role.capitalize() + ": " + entity.get(role).get("fn"))
                            case _:
                                continue
                        if entity.get(role).get("iana_id"):
                            print(role.capitalize() + " IANA ID: " + entity.get(role).get("iana_id"))
                            if "iana_id" not in printed:
                                printed["iana_id"] = 1
                        if "registrar" not in printed:
                            printed["registrar"] = 1
                    if role == "abuse":
                        match vcard_elem:
                            case "email":
                                print("Registrar Abuse Conctact Email: " + entity.get(role).get("email"))
                            case "tel":
                                print("Registrar Abuse Contact Phone: " + entity.get(role).get("tel")[4:])
                            case _:
                                pass
                        if "abuse" not in printed:
                            printed["abuse"] = 1

    if whois_data.get("eppcodes"):
        for eppcode in whois_data.get("eppcodes"):
            print("Domain Status: " + eppcode)
        if "eppcodes" not in printed:
            printed["eppcodes"] = 1

    # different registrant/admin/tech infos
    if whois_data.get("entities"):
        for entity in whois_data.get("entities"):
            if entity.get("registrar") or entity.get("abuse"):
                continue
            for role in entity:

                if role not in printed:
                    printed[role] = 1
                for vcard_elem in entity.get(role):
                    match vcard_elem:
                        case "fn":
                            print(role.capitalize() + " Name: " + entity.get(role).get("fn"))
                            continue
                        case "org":
                            print(role.capitalize() + " Organization: " + entity.get(role).get("org"))
                            continue

                        case "adr":
                            for adr_elem in entity.get(role).get("adr"):
                                match adr_elem:
                                    case "PoBox":
                                        print(
                                            role.capitalize() + " PO Box: " + entity.get(role).get("adr").get(adr_elem))
                                        continue
                                    case "extendedAddress":
                                        print(
                                            role.capitalize() + " Extended Address: " + entity.get(role).get("adr").get(
                                                adr_elem))
                                        continue
                                    case "street":
                                        for street in entity.get(role).get("adr").get(adr_elem):
                                            if street:
                                                print(role.capitalize() + " Street: " + street)
                                        continue
                                    case "locality":
                                        print(role.capitalize() + " City: " + entity.get(role).get("adr").get(adr_elem))
                                        continue
                                    case "region":
                                        print(role.capitalize() + " State/Province: " + entity.get(role).get("adr").get(
                                            adr_elem))
                                        continue
                                    case "code":
                                        print(role.capitalize() + " Postal Code: " + entity.get(role).get("adr").get(
                                            adr_elem))
                                        continue
                                    case "country":
                                        print(role.capitalize() + " Country: " + entity.get(role).get("adr").get(
                                            adr_elem))
                                        continue
                                    case _:
                                        continue

                        case "tel":
                            print(role.capitalize() + " Telephone: " + entity.get(role).get("tel")[4:])
                            continue
                        case "email":
                            print(role.capitalize() + " Email: " + entity.get(role).get("email"))
                            continue
                        case "unrecognized":
                            if entity.get(role).get("unrecognized"):
                                for elem_unrecognized in entity.get(role).get("unrecognized"):
                                    if elem_unrecognized not in unrecognized:
                                        unrecognized[elem_unrecognized] = 1
                                    else:
                                        unrecognized[elem_unrecognized] += 1
                                pass  # maybe try to show something after the whois translation displayed
                        case "errors":
                            if entity.get(role).get("errors"):
                                for elem_error in entity.get(role).get("errors"):
                                    if elem_error not in errors:
                                        errors[elem_error] = 1
                                    else:
                                        errors[elem_error] += 1
                        case _:
                            continue

    if whois_data.get("nameservers"):
        for ns in whois_data.get("nameservers"):
            print("Name Server: " + ns)
            if "nameservers" not in printed:
                printed["nameservers"] = 1
    if whois_data.get("secure_dns"):
        print("Secure DNS: " + whois_data.get("secure_dns"))
        if "secure_dns" not in printed:
            printed["secure_dns"] = 1
    print("\n\n")
    return unrecognized, errors, printed


def get_rdap_data(sample_json):
    ## rejecting the cases where analysis of the RDAP response will be useless/impossible ##
    if sample_json.get("mode") != "rdap":
        print("INFO: Sample with a mode not fitting (!=rdap), skipping")
        return "not_rdap",{}
    if sample_json.get("status_code")[0] != "200":
        print("INFO: Sample with a status code not fitting (!=200), skipping")
        return "not_OK", {}
    if sample_json.get("val") == "Cannot read the body":
        print("INFO: Sample with RDAP response body not readable, skipping")
        return "response_unreadable", {}
    lookup_sample = json.loads(sample_json.get("val"))
    print("FROM RDAP:\n\n")
    #pprint(lookup_sample)
    print("\n\n TO WHOIS: \n\n")
    whois_data = {}
    for elem in lookup_sample:
        match elem:
            case "handle":
                whois_data["registry_domain_id"] = lookup_sample.get(elem)
            case "ldhName":
                print(lookup_sample.get(elem))
                whois_data["domain_name"] = lookup_sample.get(elem)
            case "links":
                for link in lookup_sample.get("links"):
                    if link.get("rel") != "self" and link.get("type") == "application/rdap+json":
                        whois_data["registrar_rdap_server"] = tldextract.extract(link.get("href")).fqdn
            case "nameservers":
                whois_data["nameservers"] = []
                for ns in lookup_sample.get("nameservers"):
                    whois_data["nameservers"].append(ns.get("ldhName"))
            case "secureDNS":
                whois_data["secure_dns"] = "signedDelegation" if lookup_sample.get(elem).get(
                    "delegationSigned") == True else "unsigned"
            case "events":
                for event in lookup_sample.get("events"):
                    match event.get("eventAction"):
                        case "registration":
                            whois_data["registrationDate"] = event.get("eventDate")
                        case "expiration":
                            whois_data["expirationDate"] = event.get("eventDate")
                        case "last changed":
                            whois_data["lastChangedDate"] = event.get("eventDate")
                        case _:
                            continue
            case "entities":
                whois_data["entities"] = []
                for entity in lookup_sample.get("entities"):
                    roles = entity.get("roles")
                    for role in roles:
                        #pprint(entity)
                        if entity.get("vcardArray"):
                            whois_data["entities"].append(
                                {role: vcard.extract_info_from_vcard(entity.get("vcardArray")[1])})
                        if role == "registrar":
                            if entity.get("publicIds"):
                                for publicid in entity.get("publicIds"):
                                    if publicid.get("type") == "IANA Registrar ID":
                                        for whois_role in whois_data['entities']:
                                            if whois_role.get(role):
                                                whois_role[role]["iana_id"] = publicid.get("identifier")
                            if entity.get("entities"):
                                for registrar_entity in entity.get("entities"):
                                    if "abuse" in registrar_entity.get("roles"):
                                        whois_data["entities"].append({"abuse": vcard.extract_info_from_vcard(
                                            registrar_entity.get("vcardArray")[1])})

                continue

            case "status":
                with open("rdap-json-values-status.csv", 'r') as file:
                    csvfile = csv.DictReader(file, delimiter=",")
                    listed_epp = list(csvfile)
                epp_code_statuses = []

                # get only the list of EPPs that has a defined EPPCode to return in whois format
                for epp in listed_epp:
                    if epp['EPPCode'] is not None and epp['Type'] == "status":
                        epp_code_statuses.append(epp)
                whois_data["eppcodes"] = []
                # get each status line, compare it with the list of EPP status codes created just before
                for status in lookup_sample.get(elem):
                    for eppcode in listed_epp:
                        if eppcode['Value'] == status:
                            whois_data["eppcodes"].append(eppcode.get("EPPCode"))
                            break
                continue
            case _:
                continue
    # print("\n\nWHOISDATA:\n")
    # pprint(whois_data)
    # print("\n")
    return "", whois_data


with open("RDAP_sample.json", "r") as samplefile:
    unrecognized_vcards = {}
    error_dict = {}
    printed_dict = {}
    rejection_dict= {}
    nbsamples = 0
    for content in tqdm(samplefile, total=2259637):
        try:
            rejection_reason,retrieved_data = get_rdap_data(json.loads(content))
        except:
            retrieved_data = None
            continue
        if rejection_reason:
            if rejection_reason in rejection_dict:
                rejection_dict[rejection_reason] += 1
            else:
                rejection_dict[rejection_reason] = 1
            continue
        if retrieved_data:
            nbsamples+=1
            unrec_list, errors_list, printed_list = display_whois_data(retrieved_data)
            for elem_unrecognized_rn in unrec_list:
                if elem_unrecognized_rn not in unrecognized_vcards:
                    unrecognized_vcards[elem_unrecognized_rn] = 1
                else:
                    unrecognized_vcards[elem_unrecognized_rn] += 1
            for elem_error in errors_list:
                if elem_error not in error_dict:
                    error_dict[elem_error] = 1
                else:
                    error_dict[elem_error] += 1
            for printed_elem in printed_list:
                if printed_elem not in printed_dict:
                    printed_dict[printed_elem] = printed_list[printed_elem]
                else:
                    printed_dict[printed_elem] += printed_list[printed_elem]

    outputfp = open('output.txt', 'a')
    print("\n\nFor " + str(nbsamples) + " samples tested, rejected reasons of lines in RDAP_sample.json file:",file=outputfp)
    print(rejection_dict, file=outputfp)
    print("For " + str(nbsamples) + " samples tested, unrecognized properties in vCards:", file=outputfp)
    print(unrecognized_vcards, file=outputfp)
    print("\n\nFor " + str(nbsamples) + " samples tested, errors in vCards:", file=outputfp)
    print(error_dict, file=outputfp)
    print("\n\nFor " + str(nbsamples) + " samples tested, fields printed in WHOIS-to-RDAP translation:", file=outputfp)
    print(printed_dict, file=outputfp)

    outputfp.close()