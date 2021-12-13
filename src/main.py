import requests
from bs4 import BeautifulSoup
from xml.dom import minidom

SOURCE_URL = "https://tfl.gov.uk/tfl/syndication/feeds/cycle-hire/livecyclehireupdates.xml"
SOURCE_PATH = "station"

FIELDS = [
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

TARGET_NAME = "London Cycle Hire Stations"
TARGET_PATH = "../data/stations.kml"


def process_source():
    result = requests.get(SOURCE_URL)
    xml = result.content

    soup = BeautifulSoup(xml, features="lxml")
    results = soup.select(SOURCE_PATH)

    items = []
    for data in results:
        item = {}
        for field in FIELDS:
            item[field] = data.select(field)[0].string
        items.append(item)

    return items


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


def populate_items_kml(kml, document, items):
    for item in items:
        placemark = create_placemark(kml, item)
        if placemark:
            document.appendChild(placemark)

    return kml


def create_placemark(kml, item):
    if "lat" not in item or "long" not in item:
        return

    placemark = init_placemark(kml)
    set_placemark_point(kml, placemark, item["lat"], item["long"])
    add_placemark_extended_data(kml, placemark, item)
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
    latlong = "{},{}".format(long, lat)
    coordinates.appendChild(kml.createTextNode(latlong))
    point.appendChild(coordinates)


def add_placemark_extended_data(kml, placemark, item):
    EXTENDED_DATA_TAG = "ExtendedData"
    DATA_TAG = "Data"
    NAME_ATTR = "name"
    VALUE_TAG = "value"

    extended = kml.createElement(EXTENDED_DATA_TAG)
    placemark.appendChild(extended)

    for field in FIELDS:
        if item[field]:
            data = kml.createElement(DATA_TAG)
            data.setAttribute(NAME_ATTR, field)
            value = kml.createElement(VALUE_TAG)
            data.appendChild(value)
            text = kml.createTextNode(item[field])
            value.appendChild(text)
            extended.appendChild(data)


def save_kml(kml):
    file = open(TARGET_PATH, "w")
    content = kml.toprettyxml()
    file.write(content)
    file.close()


def main():
    items = process_source()
    kml, document = init_kml(TARGET_NAME)
    populate_items_kml(kml, document, items)
    save_kml(kml)


main()
