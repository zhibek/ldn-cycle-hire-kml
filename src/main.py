import requests
from bs4 import BeautifulSoup
from xml.dom import minidom

SOURCE_URL = "https://tfl.gov.uk/tfl/syndication/feeds/cycle-hire/livecyclehireupdates.xml"
SOURCE_PATH = "station"
SOURCE_FIELDS = [
    "id",
    "name",
    "terminalName",
    "lat",
    "long",
    "installed",
    "locked",
    "installDate",
    "removalDate",
    "temporary",
    "nbBikes",
    "nbEmptyDocks",
    "nbDocks",
]

TARGETS = [
    {
        "name": "London Cycle Hire Stations",
        "path": "../data/london_cycle_hire_stations.kml",
        "fields": ["id", "installed", "locked", "temporary"],
    },
    {
        "name": "London Cycle Hire Stations (Full)",
        "path": "../data/london_cycle_hire_stations_full.kml",
        "fields": SOURCE_FIELDS,
    },
]


def process_source():
    print("Requesting URL: {}".format(SOURCE_URL))
    result = requests.get(SOURCE_URL)
    xml = result.content

    soup = BeautifulSoup(xml, features="lxml")
    results = soup.select(SOURCE_PATH)
    print("Found {} results".format(len(results)))

    items = []
    for data in results:
        item = {}
        for field in SOURCE_FIELDS:
            item[field] = data.select(field)[0].string
        items.append(item)

    return items


def generate_kmls(items, targets):
    for target in targets:
        generate_kml(items, target["name"], target["path"], target["fields"])


def generate_kml(items, name, path, fields):
    print("Generate KML: {}".format(name))
    kml, document = init_kml(name)
    populate_items_kml(kml, document, items, fields)
    save_kml(kml, path)


def init_kml(title=""):
    KML_TAG = "kml"
    DOCUMENT_TAG = "Document"
    NS_ATTR = "xmlns"
    KML_NS = "http://www.opengis.net/kml/2.2"
    NAME_TAG = "name"

    kml = minidom.Document()

    root = kml.createElementNS(KML_NS, KML_TAG)
    root.setAttribute(NS_ATTR, KML_NS)
    root = kml.appendChild(root)

    document = kml.createElement(DOCUMENT_TAG)
    document = root.appendChild(document)

    if (title):
        name = kml.createElement(NAME_TAG)
        text = kml.createTextNode(title)
        name.appendChild(text)
        document.appendChild(name)

    return kml, document


def populate_items_kml(kml, document, items, fields):
    count = 0
    for item in items:
        placemark = create_placemark(kml, item, fields)
        if placemark:
            document.appendChild(placemark)
            count += 1

    print("Populated {} items".format(count))
    return kml


def create_placemark(kml, item, fields):
    if "lat" not in item or "long" not in item:
        return

    placemark = init_placemark(kml)
    set_placemark_point(kml, placemark, item["lat"], item["long"])
    set_placemark_name(kml, placemark, item["name"])
    add_placemark_extended_data(kml, placemark, item, fields)
    return placemark


def init_placemark(kml):
    PLACEMARK_TAG = "Placemark"

    placemark = kml.createElement(PLACEMARK_TAG)
    return placemark


def set_placemark_point(kml, placemark, lat, long):
    POINT_TAG = "Point"
    COORDINATES_TAG = "coordinates"

    point = kml.createElement(POINT_TAG)
    placemark.appendChild(point)
    coordinates = kml.createElement(COORDINATES_TAG)
    value = "{},{}".format(long, lat)
    text = kml.createTextNode(value)
    coordinates.appendChild(text)
    point.appendChild(coordinates)


def set_placemark_name(kml, placemark, name):
    NAME_TAG = "name"

    data = kml.createElement(NAME_TAG)
    text = kml.createTextNode(name)
    data.appendChild(text)
    placemark.appendChild(data)


def add_placemark_extended_data(kml, placemark, item, fields):
    EXTENDED_DATA_TAG = "ExtendedData"
    DATA_TAG = "Data"
    NAME_ATTR = "name"
    VALUE_TAG = "value"

    if not fields:
        return

    extended = kml.createElement(EXTENDED_DATA_TAG)
    placemark.appendChild(extended)

    for field in fields:
        if item[field] and field != "name":
            data = kml.createElement(DATA_TAG)
            data.setAttribute(NAME_ATTR, field)
            value = kml.createElement(VALUE_TAG)
            data.appendChild(value)
            text = kml.createTextNode(item[field])
            value.appendChild(text)
            extended.appendChild(data)


def save_kml(kml, path):
    file = open(path, "w")
    content = kml.toprettyxml()
    file.write(content)
    file.close()


def main():
    print("Starting process...")
    items = process_source()
    generate_kmls(items, TARGETS)
    print("Process ended!")


main()
