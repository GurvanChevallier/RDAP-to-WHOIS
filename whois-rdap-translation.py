from pprint import pprint

import vcard
import csv
import tldextract
import json
nbsamples = 2

def display_whois_data(whois_data):
    unrecognized = []
    if whois_data.get("domain_name"):
        print("Domain Name: " + whois_data.get("domain_name"))
    if whois_data.get("registry_domain_id"):
        print("Registry Domain ID: " + whois_data.get("registry_domain_id"))
    if whois_data.get("registrar_rdap_server"):
        print("Registrat RDAP Server: " + whois_data.get("registrar_rdap_server"))
    if whois_data.get("lastChangedDate"):
        print("Updated Date : " + whois_data.get("lastChangedDate"))
    if whois_data.get("creationDate"):
        print("Creation Date : " + whois_data.get("creationDate"))
    if whois_data.get("expirationDate"):
        print("Registrar Registration Exipration Date : " + whois_data.get("expirationDate"))
    # TODO: REGISTRAR INFOS TO PRINT, ESPECIALLY THE ABUSE THINGY
    #pprint()
    #print("REGISTRAR EXISTS, NEED TO BE IMPLEMENTED SOON")
    if whois_data.get("eppcodes"):
        for eppcode in whois_data.get("eppcodes"):
            print("Domain Status: "+ eppcode)

     #different registrant/admin/tech infos
    if whois_data.get("entities"):
        for entity in whois_data.get("entities"):
            if entity.get("registrar"):
                continue
            for role in entity:
                for vcard_elem in entity.get(role):
                    match vcard_elem:
                        case "fn":
                            print(role.capitalize() + " Name: " + entity.get(role).get("org"))
                            continue
                        case "org":
                            print (role.capitalize() + " Organization: " + entity.get(role).get("org"))
                            continue

                        case "adr":
                            for adr_elem in entity.get(role).get("adr"):
                                match adr_elem:
                                    case "PoBox":
                                        print(role.capitalize() + " PO Box: " + entity.get(role).get("adr").get(adr_elem))
                                        continue
                                    case "extendedAddress":
                                        print(role.capitalize() + " Extended Address: " + entity.get(role).get("adr").get(adr_elem))
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
                                        print(role.capitalize() + " State/Province: " + entity.get(role).get("adr").get(adr_elem))
                                        continue
                                    case "code":
                                        print(role.capitalize() + " Postal Code: " + entity.get(role).get("adr").get(adr_elem))
                                        continue
                                    case "country":
                                        print(role.capitalize() + " Country: " + entity.get(role).get("adr").get(adr_elem))
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
                            if unrecognized:
                                entity.get(role).get("email")
                        case _:
                            continue

    if whois_data.get("nameservers"):
        for ns in whois_data.get("nameservers"):
            print("Name Server: "+ ns)
    if whois_data.get("secure_dns"):
        print("Secure DNS: " + whois_data.get("secure_dns"))

    return

def get_rdap_data():
    with open("RDAP_sample.json", "r") as samplefile:
        for i in range(0, int(nbsamples)):
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
            pprint(lookup_sample.get("entities"))
            whois_data = {}
            for elem in lookup_sample:
                match elem:
                    case "handle":
                        whois_data["registry_domain_id"] = lookup_sample.get(elem)
                    case "ldhName":
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
                        whois_data["secure_dns"] = "signedDelegation" if lookup_sample.get(elem).get("delegationSigned") == True else "unsigned"
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
                                whois_data["entities"].append({role: vcard.extract_info_from_vcard(entity.get("vcardArray")[1])})
                                if role == "registrar":
                                    pass # DES CHOSES A FAIRE POUR RECUPERER LE ABUSE ET LE METTRE DANS LE REGISTRAR
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
    return whois_data

retrieved_data = get_rdap_data()
display_whois_data(retrieved_data)
