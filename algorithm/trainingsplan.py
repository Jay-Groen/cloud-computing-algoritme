"""
Trainingsplan Generator Algoritme
Genereert gepersonaliseerde trainingsplannen op basis van gebruikersgegevens.
"""

from typing import Dict, Any, List


def genereer_trainingsplan(gebruiker: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genereer een gepersonaliseerd trainingsplan op basis van gebruikersgegevens.
    
    Args:
        gebruiker: Dictionary met gebruikersgegevens
        
    Returns:
        Dictionary met het trainingsplan
    """
    doel = gebruiker["trainingsdoel"]
    niveau = gebruiker["trainingsniveau"]
    frequentie = gebruiker["trainingsfrequentie"]
    duur = gebruiker["trainingsduur"]
    activiteitsniveau = gebruiker["activiteitsniveau"]
    blessures = gebruiker["blessures"]
    dagen = gebruiker["beschikbare_dagen"]

    # 1. Bepaal schema type
    if frequentie <= 2:
        schema_type = "Full body"
    elif frequentie == 3:
        schema_type = "Full body / Push Pull Legs"
    elif frequentie == 4:
        schema_type = "Upper / Lower split"
    else:
        schema_type = "Split schema"

    # 2. Bepaal trainingsfocus
    if doel == "spieropbouw":
        focus = "Krachttraining met focus op hypertrofie"
        sets = 3
        herhalingen = "8-12"
    elif doel == "kracht":
        focus = "Zware krachttraining"
        sets = 4
        herhalingen = "3-6"
    elif doel == "afvallen":
        focus = "Krachttraining gecombineerd met cardio"
        sets = 3
        herhalingen = "10-15"
    elif doel == "conditie":
        focus = "Cardio en intervaltraining"
        sets = 2
        herhalingen = "12-15"
    else:
        focus = "Algemene gezondheid en full-body training"
        sets = 2
        herhalingen = "10-15"

    # 3. Bepaal aantal oefeningen
    if duur <= 30:
        aantal_oefeningen = 4
    elif duur <= 60:
        aantal_oefeningen = 6
    else:
        aantal_oefeningen = 8

    # 4. Pas belasting aan op niveau
    if niveau == "beginner":
        intensiteit = "laag tot gemiddeld"
        rust = "90 seconden"
    elif niveau == "gemiddeld":
        intensiteit = "gemiddeld"
        rust = "60-90 seconden"
    else:
        intensiteit = "hoog"
        rust = "45-90 seconden"

    # 5. Pas aan op activiteitsniveau
    if activiteitsniveau == "laag":
        aanpassing = "Start met lager volume en bouw rustig op."
    elif activiteitsniveau == "hoog":
        aanpassing = "Gebruiker kan iets hoger volume aan."
    else:
        aanpassing = "Normaal trainingsvolume toepassen."

    # 6. Controleer blessures
    vermijd: List[str] = []
    if "knie" in blessures:
        vermijd.append("zware squats en sprongoefeningen")
    if "schouder" in blessures:
        vermijd.append("overhead press en zware schouderdrukbewegingen")
    if "rug" in blessures:
        vermijd.append("zware deadlifts en zware rugbelasting")

    # 7. Verdeel trainingen over dagen
    geplande_dagen = dagen[:frequentie]

    return {
        "schema_type": schema_type,
        "focus": focus,
        "sets": sets,
        "herhalingen": herhalingen,
        "aantal_oefeningen_per_training": aantal_oefeningen,
        "intensiteit": intensiteit,
        "rusttijd": rust,
        "activiteitsaanpassing": aanpassing,
        "vermijd_oefeningen": vermijd,
        "trainingsdagen": geplande_dagen
    }
