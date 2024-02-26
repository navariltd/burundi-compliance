

BASE_API="https://ebms.obr.gov.bi:9443/ebms_api/"

def full_api_url(end_point_url):
    full_api = f"{BASE_API}{end_point_url}"
    return full_api
