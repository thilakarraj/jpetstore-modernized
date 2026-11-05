"""Legacy JPetStore demo seed constants (from jpetstore-hsqldb-dataload.sql)."""

from decimal import Decimal

SEQUENCE_ORDERNUM = ("ordernum", 1000)

DEMO_ACCOUNT_PASSWORDS = {
    "j2ee": "j2ee",
    "ACID": "ACID",
}

ACCOUNTS = [
    {
        "userid": "j2ee",
        "email": "yourname@yourdomain.com",
        "firstname": "ABC",
        "lastname": "XYX",
        "status": "OK",
        "addr1": "901 San Antonio Road",
        "addr2": "MS UCUP02-206",
        "city": "Palo Alto",
        "state": "CA",
        "zip": "94303",
        "country": "USA",
        "phone": "555-555-5555",
    },
    {
        "userid": "ACID",
        "email": "acid@yourdomain.com",
        "firstname": "ABC",
        "lastname": "XYX",
        "status": "OK",
        "addr1": "901 San Antonio Road",
        "addr2": "MS UCUP02-206",
        "city": "Palo Alto",
        "state": "CA",
        "zip": "94303",
        "country": "USA",
        "phone": "555-555-5555",
    },
]

PROFILES = [
    {"userid": "j2ee", "langpref": "english", "favcategory": "DOGS", "mylistopt": 1, "banneropt": 1},
    {"userid": "ACID", "langpref": "english", "favcategory": "CATS", "mylistopt": 1, "banneropt": 1},
]

BANNERS = [
    ("FISH", '<image src="/jpetstore/images/banner_fish.gif">'),
    ("CATS", '<image src="/jpetstore/images/banner_cats.gif">'),
    ("DOGS", '<image src="/jpetstore/images/banner_dogs.gif">'),
    ("REPTILES", '<image src="/jpetstore/images/banner_reptiles.gif">'),
    ("BIRDS", '<image src="/jpetstore/images/banner_birds.gif">'),
]

CATEGORIES = [
    ("FISH", "Fish", '<image src="/jpetstore/images/fish_icon.gif"><font size="5" color="blue"> Fish</font>'),
    ("DOGS", "Dogs", '<image src="/jpetstore/images/dogs_icon.gif"><font size="5" color="blue"> Dogs</font>'),
    (
        "REPTILES",
        "Reptiles",
        '<image src="/jpetstore/images/reptiles_icon.gif"><font size="5" color="blue"> Reptiles</font>',
    ),
    ("CATS", "Cats", '<image src="/jpetstore/images/cats_icon.gif"><font size="5" color="blue"> Cats</font>'),
    ("BIRDS", "Birds", '<image src="/jpetstore/images/birds_icon.gif"><font size="5" color="blue"> Birds</font>'),
]

PRODUCTS = [
    ("FI-SW-01", "FISH", "Angelfish", '<image src="/jpetstore/images/fish1.gif">Salt Water fish from Australia'),
    ("FI-SW-02", "FISH", "Tiger Shark", '<image src="/jpetstore/images/fish4.gif">Salt Water fish from Australia'),
    ("FI-FW-01", "FISH", "Koi", '<image src="/jpetstore/images/fish3.gif">Fresh Water fish from Japan'),
    ("FI-FW-02", "FISH", "Goldfish", '<image src="/jpetstore/images/fish2.gif">Fresh Water fish from China'),
    ("K9-BD-01", "DOGS", "Bulldog", '<image src="/jpetstore/images/dog2.gif">Friendly dog from England'),
    ("K9-PO-02", "DOGS", "Poodle", '<image src="/jpetstore/images/dog6.gif">Cute dog from France'),
    ("K9-DL-01", "DOGS", "Dalmation", '<image src="/jpetstore/images/dog5.gif">Great dog for a Fire Station'),
    ("K9-RT-01", "DOGS", "Golden Retriever", '<image src="/jpetstore/images/dog1.gif">Great family dog'),
    ("K9-RT-02", "DOGS", "Labrador Retriever", '<image src="/jpetstore/images/dog5.gif">Great hunting dog'),
    ("K9-CW-01", "DOGS", "Chihuahua", '<image src="/jpetstore/images/dog4.gif">Great companion dog'),
    ("RP-SN-01", "REPTILES", "Rattlesnake", '<image src="/jpetstore/images/snake1.gif">Doubles as a watch dog'),
    ("RP-LI-02", "REPTILES", "Iguana", '<image src="/jpetstore/images/lizard1.gif">Friendly green friend'),
    (
        "FL-DSH-01",
        "CATS",
        "Manx",
        '<image src="/jpetstore/images/cat2.gif">Great for reducing mouse populations',
    ),
    (
        "FL-DLH-02",
        "CATS",
        "Persian",
        '<image src="/jpetstore/images/cat1.gif">Friendly house cat, doubles as a princess',
    ),
    (
        "AV-CB-01",
        "BIRDS",
        "Amazon Parrot",
        '<image src="/jpetstore/images/bird2.gif">Great companion for up to 75 years',
    ),
    ("AV-SB-02", "BIRDS", "Finch", '<image src="/jpetstore/images/bird1.gif">Great stress reliever'),
]

SUPPLIERS = [
    (1, "XYZ Pets", "AC", "600 Avon Way", "", "Los Angeles", "CA", "94024", "212-947-0797"),
    (2, "ABC Pets", "AC", "700 Abalone Way", "", "San Francisco ", "CA", "94024", "415-947-0797"),
]

ITEMS = [
    ("EST-1", "FI-SW-01", Decimal("16.50"), Decimal("10.00"), 1, "P", "Large"),
    ("EST-2", "FI-SW-01", Decimal("16.50"), Decimal("10.00"), 1, "P", "Small"),
    ("EST-3", "FI-SW-02", Decimal("18.50"), Decimal("12.00"), 1, "P", "Toothless"),
    ("EST-4", "FI-FW-01", Decimal("18.50"), Decimal("12.00"), 1, "P", "Spotted"),
    ("EST-5", "FI-FW-01", Decimal("18.50"), Decimal("12.00"), 1, "P", "Spotless"),
    ("EST-6", "K9-BD-01", Decimal("18.50"), Decimal("12.00"), 1, "P", "Male Adult"),
    ("EST-7", "K9-BD-01", Decimal("18.50"), Decimal("12.00"), 1, "P", "Female Puppy"),
    ("EST-8", "K9-PO-02", Decimal("18.50"), Decimal("12.00"), 1, "P", "Male Puppy"),
    ("EST-9", "K9-DL-01", Decimal("18.50"), Decimal("12.00"), 1, "P", "Spotless Male Puppy"),
    ("EST-10", "K9-DL-01", Decimal("18.50"), Decimal("12.00"), 1, "P", "Spotted Adult Female"),
    ("EST-11", "RP-SN-01", Decimal("18.50"), Decimal("12.00"), 1, "P", "Venomless"),
    ("EST-12", "RP-SN-01", Decimal("18.50"), Decimal("12.00"), 1, "P", "Rattleless"),
    ("EST-13", "RP-LI-02", Decimal("18.50"), Decimal("12.00"), 1, "P", "Green Adult"),
    ("EST-14", "FL-DSH-01", Decimal("58.50"), Decimal("12.00"), 1, "P", "Tailless"),
    ("EST-15", "FL-DSH-01", Decimal("23.50"), Decimal("12.00"), 1, "P", "With tail"),
    ("EST-16", "FL-DLH-02", Decimal("93.50"), Decimal("12.00"), 1, "P", "Adult Female"),
    ("EST-17", "FL-DLH-02", Decimal("93.50"), Decimal("12.00"), 1, "P", "Adult Male"),
    ("EST-18", "AV-CB-01", Decimal("193.50"), Decimal("92.00"), 1, "P", "Adult Male"),
    ("EST-19", "AV-SB-02", Decimal("15.50"), Decimal("2.00"), 1, "P", "Adult Male"),
    ("EST-20", "FI-FW-02", Decimal("5.50"), Decimal("2.00"), 1, "P", "Adult Male"),
    ("EST-21", "FI-FW-02", Decimal("5.29"), Decimal("1.00"), 1, "P", "Adult Female"),
    ("EST-22", "K9-RT-02", Decimal("135.50"), Decimal("100.00"), 1, "P", "Adult Male"),
    ("EST-23", "K9-RT-02", Decimal("145.49"), Decimal("100.00"), 1, "P", "Adult Female"),
    ("EST-24", "K9-RT-02", Decimal("255.50"), Decimal("92.00"), 1, "P", "Adult Male"),
    ("EST-25", "K9-RT-02", Decimal("325.29"), Decimal("90.00"), 1, "P", "Adult Female"),
    ("EST-26", "K9-CW-01", Decimal("125.50"), Decimal("92.00"), 1, "P", "Adult Male"),
    ("EST-27", "K9-CW-01", Decimal("155.29"), Decimal("90.00"), 1, "P", "Adult Female"),
    ("EST-28", "K9-RT-01", Decimal("155.29"), Decimal("90.00"), 1, "P", "Adult Female"),
]

INVENTORY_QTY = 10000
ITEM_IDS = [item[0] for item in ITEMS]
