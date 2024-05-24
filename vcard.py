def extract_info_from_vcard(vcard): #This extration is reducing the number of fields to only the ones that are expressed, saving potentially a lot of "" elements, in "n" or "adr" fields for an example.
    infos = {}
    for elem in vcard:
        match elem[0]:
            case "source":
                if elem[2] == "uri":
                    infos["source"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a URI value")
                    return

            case "kind":
                if elem[2] == "text":
                    infos["kind"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a TEXT value")
                    return
            case "xml":
                print("\"" + elem[0] + "\" is not implemented, as it is optional in RFC6350, but is detected.")
                continue
            case "fn": # 6.2.1
                infos["fn"] = elem[3]
            case "n": # 6.2.2
                if elem[2] == "text":
                    for i in range(0, 4):
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
                else:
                    print("ERROR: " + elem[0] + " is not a TEXT value")
                    return
            case "nickname":
                if elem[2] == "text":
                    infos["nickname"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a TEXT value")
                    return
            case "photo":
                if elem[2] == "uri":
                    infos["photo"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a URI value")
                    return
            case "bday":
                if elem[2] == "date-and-or-time" or elem[2] == "text":
                    infos["bday"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a DATE-AND-OR-TIME value")
                    return
            case "anniversary":
                if elem[2] == "date-and-or-time" or elem[2] == "text":
                    infos["anniversary"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a TEXT nor a DATE-AND-OR-TIME value")
                    return
            case "gender":
                if elem[2] == "text":
                    for i in range(0, 2):
                        if elem[3][i] != "":
                            match i:
                                case 0:
                                    if elem[3][i] in ["M", "F", "O", "N", "U"]:
                                        infos["gender"]["sex"] = elem[3][i]
                                    else:
                                        print("ERROR: " + elem[0] + " sex is not recognized within the values defined in RFC6350 Section 6.2.7")
                                        return
                                case 1:
                                    infos["gender"]["genderIdentity"] = elem[3][i]
                else:
                    print("ERROR: " + elem[0] + " is not a TEXT value")
                    return

            case "adr":
                if elem[2] == "text":
                    for i in range(0, 7):
                        if elem[3][i] != "":
                            match i:  # I followed the indications of the RFC6350 for the ADR field : https://datatracker.ietf.org/doc/html/rfc6350#section-6.3.1
                                case 0:
                                    infos["adr"]["poBox"] = elem[3][i]
                                case 1:
                                    infos["adr"]["extendedAddress"] = elem[3][i]
                                case 2:
                                    infos["adr"]["street"] = elem[3][i]
                                case 3:
                                    infos["adr"]["locality"] = elem[3][i]
                                case 4:
                                    infos["adr"]["region"] = elem[3][i]
                                case 5:
                                    infos["adr"]["code"] = elem[3][i]
                                case 6:
                                    infos["adr"]["country"] = elem[3][i]
                                case _:
                                    print("ERROR: Too many values in " + elem[0] + ".")
                                    return
                else:
                    print("ERROR: " + elem[0] + " is not a TEXT value")
                    return
            case "tel": # RFC3966 TEL URI values
                if elem[2] == "text" or elem[2] == "uri":
                    infos["tel"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a TEXT nor a URI value")
                    return
            case "email":
                if elem[2] == "text":
                    infos["email"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a TEXT nor a URI value")
                    return
            case "impp":
                if elem[2] == "uri":
                    infos["impp"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a URI value")
                    return
            case "lang":
                if elem[2] == "langage-tag":
                    infos["lang"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a LANGUAGE-TAG value")
                    return
            case "tz":
                if elem[2] == "text" or elem[2] == "uri" or elem[2] == "utc-offset":
                    infos["tz"] = elem[3]
                    if elem[2] == "utc-offset":
                        print("WARN: "+ elem[0] + " is a UTC-OFFSET value, not recommended by RFC6350")
                else:
                    print("ERROR: " + elem[0] + " is not a TEXT, URI nor a UTC-OFFSET value")
                    return
            case "geo": #RFC 5870
                if elem[2] == "uri":
                    infos["geo"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a URI value")
                    return
            case "title":
                if elem[2] == "text":
                    infos["title"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a TEXT value")
                    return
            case "role": #will be unused in RDAP, because of the roles[] values being used and defined in RFC9083
                if elem[2] == "text":
                    infos["role"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a TEXT value")
                    return
            case "logo":
                if elem[2] == "uri":
                    infos["logo"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a URI value")
                    return
            case "org":
                if elem[2] == "text":
                    if type(elem[3]) == str:
                        infos["org"] = elem[3]
                    else:
                        infos["org"]["orgName"] = elem[3][0]
                        infos["org"]["orgUnits"] = elem[3][1:]
                else:
                    print("ERROR: " + elem[0] + " is not a TEXT value")
                    return
            case "member":
                if infos.get("kind") == "group":
                    if elem[2] == "uri":
                        infos["member"] = elem[3]
                    else:
                        print("ERROR: " + elem[0] + " is not a URI value")
                        return
                else:
                    print("ERROR: " + elem[0] + " property MUST NOT be present unless the KIND property is defined as \"group\"")
                    return
            case "related": #need to take care to "related-type-value" types in RFC6350 section 6.6.6
                if elem[2] == "uri" or elem[2] == "text":
                    infos["related"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a URI nor a TEXT value")
            case "categories":
                if elem[2] == "text":
                    infos["categories"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a TEXT value")
                    return
            case "note":
                if elem[2] == "text":
                    infos["note"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a text value")
                    return
            case "prodid":
                if elem[2] == "text":
                    infos["prodid"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a TEXT value")
                    return
            case "rev":
                if elem[2] == "timestamp":
                    infos["rev"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a TIMESTAMP value")
                    return
            case "sound":
                if elem[2] == "uri":
                    infos["sound"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a URI value")
                    return
            case "uid":
                if elem[2] == "uri" or elem[2] == "text":
                    infos["uid"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a URI nor a TEXT value")
            case "clientpidmap": # seems painful to implement sect6.7.7
                print("\"" + elem[0] + "\" is not implemented yet, but is detected.")
                continue
            case "url":
                if elem[2] == "uri":
                    infos["url"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a URI value")
                    return
            case "version":
                if elem[2] == "text":
                    infos["version"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a TEXT value")
                    return
            case "key":
                if elem[2] == "text" or elem[2] == "uri":
                    infos["key"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a TEXT nor a URI value")
                    return
            case "fburl": #need the pref character if multiple instances are specified
                if elem[2] == "uri":
                    infos["fburl"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a URI value")
            case "caladruri": #need the pref character if multiple instances are specified
                if elem[2] == "uri":
                    infos["caladruri"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a URI value")
            case "caluri": #need the pref character if multiple instances are specified
                if elem[2] == "uri":
                    infos["caluri"] = elem[3]
                else:
                    print("ERROR: " + elem[0] + " is not a URI value")
            case _:
                print("ERROR: unrecognized vCard object " + elem[0])
                continue
        if infos.get("version") is None or infos.get("version") != "4.0": # RFC6350 sect. 6.7.9 (maybe not in jCard we'll see)
            print("ERROR: Version of the jCard missing/misplaced")
            return
    if not "kind" in infos:
        infos["kind"] = "individual"

    return infos