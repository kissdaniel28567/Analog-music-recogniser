POPULAR_CARTRIDGES = {
    "ortofon 2m red": 1000,
    "ortofon 2m blue": 1000,
    "audio-technica at95e": 500,
    "audio-technica vm95ml": 1000,
    "nagaoka mp-110": 800,
    "denon dl-103": 1000,
    "shure m97xe": 800
}

def lookup_cartridge_life(model_name):
    """
    Returns recommended hours. 
    1. Checks internal dictionary.
    2. (Optional) Could perform a Google Search via an API here.
    3. Defaults to 800 hours.
    """
    model_lower = model_name.lower().strip()

    for key, hours in POPULAR_CARTRIDGES.items():
        if key in model_lower or model_lower in key:
            return hours
            
    return 800