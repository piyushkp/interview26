from urllib.parse import quote

URL = "https://jsonmock.hackerrank.com/api/food_outlets?city={}&page={}"


def default_get(url):
    import requests  # imported lazily so tests run without network or requests
    return requests.get(url, timeout=10).json()


def getRelevantFoodOutlets(city, maxCost, get=default_get):
    names = []
    page, total_pages = 1, 1
    while page <= total_pages:
        body = get(URL.format(quote(city), page))
        total_pages = body.get("total_pages", 0)
        for outlet in body.get("data", []):
            if outlet["estimated_cost"] <= maxCost:
                names.append(outlet["name"])
        page += 1
    return names


if __name__ == "__main__":
    # Offline demo with a fake two-page API
    pages = {
        1: {"total_pages": 2, "data": [
            {"name": "BKC DIVE", "estimated_cost": 40},
            {"name": "Fancy Place", "estimated_cost": 90}]},
        2: {"total_pages": 2, "data": [
            {"name": "Vedge", "estimated_cost": 50}]},
    }
    fake_get = lambda url: pages[int(url.rsplit("=", 1)[1])]
    for name in getRelevantFoodOutlets("Denver", 50, fake_get):
        print(name)
