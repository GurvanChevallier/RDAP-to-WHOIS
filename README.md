# RDAP-to-WHOIS
M1 MOSIG Internship work over DNS, and especially WHOIS and RDAP protocols in networking team in LIG, DRAKKAR.

main.py is the file that i first worked on, asking for a domain to be requested in RDAP, and then translate that data to a WHOIS-like format.

vcard.py is tranforming a vcard, that is an element of a vcardArray, into a dictionnary with each element present, partially following the RFC6350, the RFC7095, and the RFC9083. It also detects errors and unrecognized parameters.
This file for now is covering almost every property listed in RFC6350 and the types the data should be in (the third object of a vcard ["property", {parameters}, "value-type", "value"). IT DOES NOT TREAT THE PARAMETERS, IMPORTANT FOR SOME CORNER CASES, like addresses put in a label parameter, different types of phones, or the preferences

sample_tests.py was a try to verify that the sample RDAP values were following the RFC rules, detect anomalies, and get a feedback.

whois_rdap_translation.py is a better try, while using the vcard.get_info_from_vcard() function in order to create the whois data. It relies less on a "hard-coded" approach, making is much more reliable on different domains and TLDs.
