from pprint import pprint

import requests
import csv
import tldextract

def retrieve_rdap_server(domain):
    # get the suffix of the fqdn entered by the user
    tld = tldextract.extract(domain).suffix

    # request it to root.rdap.org to retireve a first rdap server
    tld_rdap_lookup = "https://rdap.iana.org/domain/" + tld
    # first was https://root.rdap.org/domain/ + tld but this broke 21st may, replaced by https://rdap.iana.org/domain/ + tld
    rq = requests.get(tld_rdap_lookup)
    if rq.status_code != 200:
        return None
    else:
        list_links = rq.json().get("links")

        for link in list_links:
            if link.get("type") == "application/rdap+json":
                return link.get("href")

def entity_with_role(lookup, rolename):
    for entity in lookup["entities"]: #we check on all the entities declared
        for role in entity["roles"]: # we check on all the roles (mabe there's only one possible at a time, but unfortunately we have an array, so iteration for safety)
            if role == rolename:
                return entity

def get_vcard_elem(vcardArray, nameElement):
    if vcardArray[0] == "vcard":
        for elem in vcardArray[1]:
            if elem[0] == nameElement:
                return elem[-1]
        print("ERROR, elem not find in the vcard")
        return
    else:
        print("ERROR, can't find a vcard in the vcard array")
        return


def whois_lookup_registrar(lookup):
    print("Domain Name:", lookup['ldhName'])
    print("Registry Domain ID:", lookup['handle'])

    #in the choice of implementation, I decided that the RDAP server was way more relevant to display, because even if the datas are printed in the WHOIS plain text form, those datas are from RDAP.
    for link in lookup["links"]:
        if link["rel"] != "self" and link["href"] is not None and link["type"] == "application/rdap+json": #make sure that this is a rdap request with another server
            otherRDAP = link.get("href")
            break
    print("Registrar RDAP server: " + tldextract.extract(otherRDAP).fqdn)
    print("Registrar URL:")
    for event in lookup['events']:
        if event["eventAction"] == "registration":
            registrationDatetime = event["eventDate"]
        elif event["eventAction"] == "last changed":
            lastchangedDatetime = event["eventDate"]
        elif event["eventAction"] == "expiration":
            expirationDatetime = event["eventDate"]

    print("Updated Date:", lastchangedDatetime)
    print("Creation Date:", registrationDatetime)
    print("Registrar Registration Expiration Date:", expirationDatetime)
    entitylist = entity_with_role(lookup, "registrar")  # to get the entity that has the role registrar, and the entity with the role abuse in this first one
    print("Registrar: ", get_vcard_elem(entitylist["vcardArray"], "fn"))

    for id in entitylist["publicIds"]:
        if id.get('type') == 'IANA Registrar ID':
            ianaRegID = id.get("identifier")

    try:
        print("Registrar IANA ID: ", ianaRegID)
    except:
        print("ERROR: no IANA ID retrieved for the Registrar")

    entity = entity_with_role(entitylist, "abuse")
    abuseEmail = get_vcard_elem(entity["vcardArray"], "email")
    abuseTel = get_vcard_elem(entity["vcardArray"], "tel")
    print("Registrar Abuse Contact Email: ", abuseEmail)
    print("Registrar Abuse Contact Phone: ", abuseTel[4:]) # 4: to remove the tel: in front of every phone number in vcard format

# rdap-json-values-status.csv is originally from https://www.iana.org/assignments/rdap-json-values/rdap-json-values.xhtml, and were edited to add the EPP codes available on the RFC8056.
def whois_print_EPPs(lookup):
    # intitalise the list of all the statuses
    with open("rdap-json-values-status.csv", 'r') as file:
        csvfile = csv.DictReader(file, delimiter=",")
        listed_epp = list(csvfile)
    epp_code_statuses = []

    # get only the list of EPPs that has a defined EPPCode to return in whois format
    for epp in listed_epp:
        if epp['EPPCode'] is not None and epp['Type'] == "status":
            epp_code_statuses.append(epp)

    # get each status line, compare it with the list of EPP status codes created just before
    for elem in lookup["status"]:
        for eppcode in listed_epp:
            if eppcode['Value'] == elem:
                print("Domain Status:", eppcode.get("EPPCode"))
                break

def whois_print_registrant(lookup):
    otherRDAP = None
    for link in lookup["links"]:
        if link["rel"] != "self" and link["href"] is not None and link["type"] == "application/rdap+json": #make sure that this is a rdap request with another server
            otherRDAP = requests.get(link["href"].lower())
            break
    if otherRDAP.status_code != 200:
        print("ERROR cannot access another RDAP server referenced")
        print("therefore, no information on the registrant")
        print("Status code:"+ str(otherRDAP.status_code))
        return
    else:
        json_otherRDAP= otherRDAP.json()
        for entity in json_otherRDAP.get("entities"):
            role = ""
            match entity["roles"][0]: #list available here https://www.rfc-editor.org/rfc/rfc9083.html#sect-10.2.4
                case "registrant":
                    role = "Registrant"
                case "administrative":
                    role = "Admin"
                case "technical":
                    role = "Tech"
                case "billing":
                    role = "Billing"
                case "sponsor":
                    role = "Sponsor"
                case "registrar":
                    continue
                case _:
                    print("ERROR entity role not recognized in registrant RDAP server")
                    continue
            entity_print(role,entity) # now get the information of the different roles registered

def entity_print(role, entity):
    if role is None:
        print("ERROR: no role assigned to entity trying to be printed")
        return
    vcardArray = entity["vcardArray"]
    if vcardArray[0] != "vcard":
        print("ERROR: vcardArray missing the vcard type")
        return
    vcard = vcardArray[1]
    for elem in vcard:
        match elem[0]:
            case "version":
                continue
            case "fn":
                continue
            case "org":
                if elem[1].get("type") == "work":
                    print(role + " Organization: " + elem[3])
                continue
            case "adr":
                for i in range(0,7):
                    if elem[3][i] != "":
                        match i: # I followed the indications of the RFC6350 for the ADR field : https://datatracker.ietf.org/doc/html/rfc6350#section-6.3.1
                            case 0:
                                print(role + " PO box number: " + elem[3][i])
                            case 1:
                                print(role + " Apartment Number: " + elem[3][i])
                            case 2:
                                for line in elem[3][i]: #we can have multiple lines for the same entry, should do it for all possible entries
                                    print(role + " Street: " + line)
                            case 3:
                                print(role + " City: " + elem[3][i])
                            case 4:
                                print(role + " State/Province: " + elem[3][i])
                            case 5:
                                print(role + " Postal Code: " + elem[3][i])
                            case 6:
                                print(role + " Country: " + elem[3][i])
                            case _:
                                break
            case "tel":
                # This part is partially following the direction of the RFC6350 on the field TEL: https://datatracker.ietf.org/doc/html/rfc6350#section-6.4.1
                # The type of the telephone is not supported here, but can be implemented
                print(role + " Phone: " + elem[3][4:])
            case "email":
                print(role + " email: " + elem[3])
                continue
            case _:
                print("ERROR: unrecognized vCard object "+ elem[0])
                continue

def extract_info_from_vcard(vcard): #This extration is reducing the number of fields to only the ones that are expressed, saving potentially a lot of "" elements, in "n" or "adr" fields for an example.
    infos = {}
    for elem in vcard:
        match elem[0]:
            case "version":
                infos["version"] = elem[3]
            case "fn": # 6.2.1
                infos["fn"] = elem[3]
            case "n": # 6.2.2
                for i in range(0, 3):
                    if elem[3][i] != "":
                        match i:
                            case 0:
                                infos["n"]["familyNames"] = elem[3][i]
                            case 1:
                                infos["n"]["givenNames"] = elem[3][i]
                            case 2:
                                infos["n"]["additionalNames"] = elem[3][i]
                            case 3:
                                infos["n"]["honorificPrefixes"] = elem[3][i]
                            case 4:
                                infos["n"]["honorificSuffixes"] = elem[3][i]
            case "nickname":  # TODO: need to understand more what is going on with the "text-list" and the "list-component 4(";" list-component)" of the "n" values
                infos["nickname"] = {"type": elem[1], "nickname":elem[3]}
            case "org":
                if elem[1].get("type") is not None:
                    infos["org"] = {"type": elem[3], "":""}
            case "adr":
                for i in range(0, 7):
                    if elem[3][i] != "":
                        match i:  # I followed the indications of the RFC6350 for the ADR field : https://datatracker.ietf.org/doc/html/rfc6350#section-6.3.1
                            case 0:
                                print(role + " PO box number: " + elem[3][i])
                            case 1:
                                print(role + " Apartment Number: " + elem[3][i])
                            case 2:
                                for line in elem[3][i]:  # we can have multiple lines for the same entry, should do it for all possible entries
                                    print(role + " Street: " + line)
                            case 3:
                                print(role + " City: " + elem[3][i])
                            case 4:
                                print(role + " State/Province: " + elem[3][i])
                            case 5:
                                print(role + " Postal Code: " + elem[3][i])
                            case 6:
                                print(role + " Country: " + elem[3][i])
                            case _:
                                break
            case "tel":
                # This part is partially following the direction of the RFC6350 on the field TEL: https://datatracker.ietf.org/doc/html/rfc6350#section-6.4.1
                # The type of the telephone is not supported here, but can be implemented
                print(role + " Phone: " + elem[3][4:])
            case "email":
                print(role + " email: " + elem[3])
                continue
            case _:
                print("ERROR: unrecognized vCard object " + elem[0])
                continue


def whois_nameservers(lookup): #prints the nameservers and the status of the dnssec
    for elem in lookup["nameservers"]:
        if elem["objectClassName"] == "nameserver":
            print("Name Server: ", elem["ldhName"].lower())

    if not lookup["secureDNS"].get("delegationSigned"):
        print("DNSSEC: unsigned")
    else:
        print("DNSSEC: delegationSigned")

def main():
    domain = input("RDAP-to-WHOIS | Enter domain to process: ")
    rdap_lookup_server = retrieve_rdap_server(domain)
    if rdap_lookup_server is None:
        print("ERROR when trying to retrieve the RDAP server of the TLD")
        return
    #print(rdap_lookup_server)
    rdap_lookup_domain = rdap_lookup_server + "domain/" + domain
    request = requests.get(rdap_lookup_domain)
    if request.status_code != 200:
        print("ERROR in the request to the RDAP server")
        return
    else:
        print('\nRDAP read:\n')
        json_rdap = request.json()
        pprint(json_rdap)
        print('\n\nWhois translated:\n')
        whois_lookup_registrar(json_rdap)
        whois_print_EPPs(json_rdap)
        whois_print_registrant(json_rdap)
        # TODO: registrant informations to complete
        # TODO: support of different profiles (for example admin, tech, etc.... (probably through a support of the different parts with a switch case that will have to first check that the MANDATORY informations are there to print, then do all the options :'(   ))
        whois_nameservers(json_rdap)
    # whois_print(rdap_lookup)

if __name__ == "__main__":
    main()