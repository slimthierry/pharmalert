"""
ATC (Anatomical Therapeutic Chemical) classification system.
Reference codes for medication classification used in the WHO system.
"""

# ATC Level 1 - Anatomical main group
ATC_LEVEL1 = {
    "A": "Appareil digestif et metabolisme",
    "B": "Sang et organes hematopoietiques",
    "C": "Systeme cardiovasculaire",
    "D": "Dermatologie",
    "G": "Systeme genito-urinaire et hormones sexuelles",
    "H": "Hormones systemiques (hors hormones sexuelles et insulines)",
    "J": "Anti-infectieux generaux a usage systemique",
    "L": "Antineoplasiques et immunomodulateurs",
    "M": "Systeme musculo-squelettique",
    "N": "Systeme nerveux",
    "P": "Antiparasitaires, insecticides et repulsifs",
    "R": "Systeme respiratoire",
    "S": "Organes sensoriels",
    "V": "Divers",
}

# Common ATC codes used in hospital settings
COMMON_ATC_CODES = {
    # Cardiovascular
    "C01AA05": {"name": "Digoxine", "group": "Glycosides cardiaques"},
    "C03CA01": {"name": "Furosemide", "group": "Diuretiques de l'anse"},
    "C07AB02": {"name": "Metoprolol", "group": "Beta-bloquants selectifs"},
    "C07AB03": {"name": "Atenolol", "group": "Beta-bloquants selectifs"},
    "C08CA01": {"name": "Amlodipine", "group": "Inhibiteurs calciques"},
    "C09AA02": {"name": "Enalapril", "group": "Inhibiteurs de l'ECA"},
    "C09AA05": {"name": "Ramipril", "group": "Inhibiteurs de l'ECA"},
    "C10AA01": {"name": "Simvastatine", "group": "Statines"},
    "C10AA05": {"name": "Atorvastatine", "group": "Statines"},

    # Nervous system
    "N02AA01": {"name": "Morphine", "group": "Opioides naturels"},
    "N02AA05": {"name": "Oxycodone", "group": "Opioides naturels"},
    "N02BA01": {"name": "Acide acetylsalicylique", "group": "Analgesiques"},
    "N02BE01": {"name": "Paracetamol", "group": "Analgesiques"},
    "N05BA01": {"name": "Diazepam", "group": "Benzodiazepines"},
    "N05BA06": {"name": "Lorazepam", "group": "Benzodiazepines"},
    "N05CF01": {"name": "Zopiclone", "group": "Hypnotiques"},
    "N06AB06": {"name": "Sertraline", "group": "ISRS"},

    # Anti-infectives
    "J01CA04": {"name": "Amoxicilline", "group": "Penicillines"},
    "J01CR02": {"name": "Amoxicilline + Acide clavulanique", "group": "Penicillines + inhibiteur"},
    "J01FA09": {"name": "Clarithromycine", "group": "Macrolides"},
    "J01MA02": {"name": "Ciprofloxacine", "group": "Fluoroquinolones"},
    "J01XD01": {"name": "Metronidazole", "group": "Imidazoles"},

    # Blood
    "B01AA03": {"name": "Warfarine", "group": "Antivitamines K"},
    "B01AB01": {"name": "Heparine", "group": "Heparines"},
    "B01AF01": {"name": "Rivaroxaban", "group": "Anticoagulants oraux directs"},
    "B01AF02": {"name": "Apixaban", "group": "Anticoagulants oraux directs"},
    "B01AC06": {"name": "Acide acetylsalicylique (antiplaquettaire)", "group": "Antiplaquettaires"},

    # Digestive
    "A02BC01": {"name": "Omeprazole", "group": "Inhibiteurs pompe a protons"},
    "A02BC05": {"name": "Esomeprazole", "group": "Inhibiteurs pompe a protons"},
    "A10BA02": {"name": "Metformine", "group": "Biguanides"},
    "A10AB01": {"name": "Insuline humaine rapide", "group": "Insulines"},

    # Musculoskeletal
    "M01AE01": {"name": "Ibuprofene", "group": "AINS"},
    "M01AE02": {"name": "Naproxene", "group": "AINS"},
    "M01AB05": {"name": "Diclofenac", "group": "AINS"},

    # Respiratory
    "R03AC02": {"name": "Salbutamol", "group": "Beta-2 agonistes inhales"},
    "R03BA02": {"name": "Budesonide", "group": "Corticoides inhales"},
    "R06AE07": {"name": "Cetirizine", "group": "Antihistaminiques"},
}


def get_atc_group(atc_code: str) -> str:
    """Get the anatomical main group name for an ATC code."""
    if not atc_code:
        return "Non classe"
    first_letter = atc_code[0].upper()
    return ATC_LEVEL1.get(first_letter, "Non classe")


def get_atc_info(atc_code: str) -> dict:
    """Get detailed info for a specific ATC code."""
    return COMMON_ATC_CODES.get(atc_code, {"name": "Inconnu", "group": "Non reference"})


def search_atc_codes(query: str) -> list:
    """Search ATC codes by name or code."""
    query_lower = query.lower()
    results = []
    for code, info in COMMON_ATC_CODES.items():
        if (
            query_lower in code.lower()
            or query_lower in info["name"].lower()
            or query_lower in info["group"].lower()
        ):
            results.append({"code": code, **info})
    return results
