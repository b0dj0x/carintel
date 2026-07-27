#!/usr/bin/env python3
"""
CarIntel — License Plate OSINT · Vehicle History · VIN Decoder
"""

import sys, os, json, time, argparse, re
from datetime import datetime, timezone
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except ImportError:
    sys.exit("[!] pip install requests")
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    from rich import box
except ImportError:
    sys.exit("[!] pip install rich")

console = Console()
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ASCII = [
    " ██████╗██████╗  █████╗ ██╗███╗   ██╗███████╗██╗      ██████╗██╗  ██╗",
    "██╔════╝██╔══██╗██╔══██╗██║████╗  ██║██╔════╝██║     ██╔════╝██║  ██║",
    "██║     ██████╔╝███████║██║██╔██╗ ██║█████╗  ██║     ██║     ███████║",
    "██║     ██╔══██╗██╔══██║██║██║╚██╗██║██╔══╝  ██║     ██║     ██╔══██║",
    "╚██████╗██║  ██║██║  ██║██║██║ ╚████║██║     ███████╗╚██████╗██║  ██║",
    " ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝",
]

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"

# ═══════════════════════════════════════════════════════════════
#  VIN DECODER DATABASE
# ═══════════════════════════════════════════════════════════════

VIN_WMI = {
    "1FA": "Ford Motor Company (USA)",
    "1FB": "Ford Motor Company (USA)",
    "1FC": "Ford Motor Company (USA)",
    "1FD": "Ford Motor Company (USA)",
    "1FM": "Ford Motor Company (USA)",
    "1FT": "Ford Motor Company (USA)",
    "1G1": "Chevrolet (USA)",
    "1GC": "Chevrolet Truck (USA)",
    "1GT": "GMC Truck (USA)",
    "1G6": "Cadillac (USA)",
    "1G8": "Saturn (USA)",
    "1GN": "Chevrolet SUV (USA)",
    "1HG": "Honda (USA)",
    "1J4": "Jeep (USA)",
    "1J8": "Jeep (USA)",
    "1LN": "Lincoln (USA)",
    "1ME": "Mercury (USA)",
    "1N4": "Nissan (USA)",
    "1N6": "Nissan Truck (USA)",
    "1NX": "NUMMI/Toyota (USA)",
    "1VW": "Volkswagen (USA)",
    "1ZV": "Ford (USA)",
    "2FA": "Ford Motor Company (Canada)",
    "2G1": "Chevrolet (Canada)",
    "2HG": "Honda (Canada)",
    "2HM": "Hyundai (Canada)",
    "2T1": "Toyota (Canada)",
    "3FA": "Ford Motor Company (Mexico)",
    "3G1": "Chevrolet (Mexico)",
    "3VW": "Volkswagen (Mexico)",
    "4T1": "Toyota (USA)",
    "4T3": "Toyota Van (USA)",
    "4T4": "Toyota SUV (USA)",
    "5FN": "Honda SUV (USA)",
    "5J6": "Honda (USA)",
    "5NP": "Hyundai (USA)",
    "5TD": "Hyundai SUV (USA)",
    "JDA": "Daihatsu (Japan)",
    "JF1": "Subaru (Japan)",
    "JF2": "Subaru (Japan)",
    "JG": "Holden (Australia)",
    "JH": "Honda (Japan)",
    "JK": "Kawasaki (Japan)",
    "JL": "Suzuki (Japan)",
    "JM": "Mazda (Japan)",
    "JN": "Nissan (Japan)",
    "JS": "Suzuki (Japan)",
    "JT": "Toyota (Japan)",
    "JY": "Yamaha (Japan)",
    "KL": "Daewoo/GM Korea",
    "KMH": "Hyundai (Korea)",
    "KNA": "Kia (Korea)",
    "KNE": "Kia (Korea)",
    "KNJ": "Kia (Korea)",
    "KNM": "SsangYong (Korea)",
    "LA6": "Mitsubishi (China)",
    "LBV": "BMW Brilliance (China)",
    "LDC": "Dongfeng Citroen (China)",
    "LDN": "Nissan (China)",
    "LE1": "Honda (China)",
    "LFV": "FAW-Volkswagen (China)",
    "LGB": "Dongfeng Nissan (China)",
    "LJC": "JAC (China)",
    "LL0": "Lifan (China)",
    "LMG": "Great Wall (China)",
    "LPA": "Changan PSA (China)",
    "LPS": "SAIC (China)",
    "LTV": "FAW Toyota (China)",
    "LVG": "GAC Toyota (China)",
    "LVR": "Changan Ford (China)",
    "LVS": "Changan Suzuki (China)",
    "LVV": "Chery (China)",
    "LZW": "SAIC-GM-Wuling (China)",
    "MA1": "Mahindra (India)",
    "MA3": "Maruti Suzuki (India)",
    "MA6": "Renault Nissan (India)",
    "MB8": "Tata Motors (India)",
    "MCA": "Fiat India",
    "MHB": "Mercedes-Benz India",
    "MMB": "Bajaj Auto (India)",
    "MMC": "Tata Motors (India)",
    "NLA": "Mercedes-Benz (Germany)",
    "NLC": "Mercedes-Benz Vans (Germany)",
    "NLF": "Fiat (Germany)",
    "NLH": "Hyundai Europe (Germany)",
    "NLT": "Tesla (Netherlands)",
    "SAJ": "Jaguar (UK)",
    "SAL": "Land Rover (UK)",
    "SAV": "BMW UK",
    "SAZ": "Rolls-Royce (UK)",
    "SCC": "Lotus (UK)",
    "SCF": "Aston Martin (UK)",
    "SCM": "MG Rover (UK)",
    "SDB": "Nissan Europe (UK)",
    "SFP": "Aston Martin (UK)",
    "SFZ": "Aston Martin (UK)",
    "SGB": "SsangYong (UK)",
    "SJJ": "Jaguar Land Rover (UK)",
    "SKF": "Toyota Manufacturing UK",
    "TMA": "Hyundai Motor Manufacturing Czech",
    "TRU": "Audi (Hungary)",
    "TSE": "Skoda (Czech Republic)",
    "TSM": "Skoda Auto (Czech Republic)",
    "TTV": "Suzuki Hungary",
    "UF9": "Iveco (Turkey)",
    "WAU": "Audi (Germany)",
    "WBA": "BMW (Germany)",
    "WBY": "BMW i (Germany)",
    "WDB": "Mercedes-Benz (Germany)",
    "WDZ": "Mercedes-Benz (Germany)",
    "WFR": "Renault (Germany)",
    "WKE": "MAN (Germany)",
    "WMA": "MAN Trucks (Germany)",
    "WMB": "MAN Bus (Germany)",
    "WP0": "Porsche (Germany)",
    "WUA": "Audi (Germany)",
    "WVW": "Volkswagen (Germany)",
    "WV1": "Volkswagen Commercial (Germany)",
    "WV2": "Volkswagen Bus/Van (Germany)",
    "WV3": "Volkswagen Truck (Germany)",
    "ZAM": "Maserati (Italy)",
    "ZAP": "Alfa Romeo (Italy)",
    "ZAR": "Alfa Romeo (Italy)",
    "ZFF": "Ferrari (Italy)",
    "ZLA": "Lamborghini (Italy)",
    "ZOM": "Automobili Pininfarina (Italy)",
}

VIN_YEAR = {
    "A": 2010, "B": 2011, "C": 2012, "D": 2013, "E": 2014,
    "F": 2015, "G": 2016, "H": 2017, "J": 2018, "K": 2019,
    "L": 2020, "M": 2021, "N": 2022, "P": 2023, "R": 2024,
    "S": 2025, "T": 2026, "V": 2027, "W": 2028, "X": 2029,
    "Y": 2030, "1": 2031, "2": 2032, "3": 2033, "4": 2034,
    "5": 2035, "6": 2036, "7": 2037, "8": 2038, "9": 2039,
}

VIN_YEAR_OLD = {
    "1": 2001, "2": 2002, "3": 2003, "4": 2004, "5": 2005,
    "6": 2006, "7": 2007, "8": 2008, "9": 2009,
}

# ═══════════════════════════════════════════════════════════════
#  STATE/COUNTRY PLATE FORMATS
# ═══════════════════════════════════════════════════════════════

PLATE_FORMATS = {
    "Alabama": {"pattern": r"^\d{1,4}[A-Z]{3}$", "format": "1234ABC", "example": "1234ABC"},
    "Alaska": {"pattern": r"^\d{3}[A-Z]{3}$", "format": "123ABC", "example": "123ABC"},
    "Arizona": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Arkansas": {"pattern": r"^\d{3}[A-Z]{3}$", "format": "123ABC", "example": "123ABC"},
    "California": {"pattern": r"^\d[A-Z]{3}\d{4}$", "format": "1ABC1234", "example": "1ABC1234"},
    "Colorado": {"pattern": r"^[A-Z]{2}-\d{4}$", "format": "AB-1234", "example": "AB-1234"},
    "Connecticut": {"pattern": r"^[A-Z]{2,3}\d{4}$", "format": "AB1234", "example": "AB1234"},
    "Delaware": {"pattern": r"^\d{5,6}$", "format": "123456", "example": "123456"},
    "Florida": {"pattern": r"^[A-Z]{3}\d{4}[A-Z]$", "format": "ABC123D", "example": "ABC123D"},
    "Georgia": {"pattern": r"^[A-Z]{3}[A-Z]?\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Hawaii": {"pattern": r"^[A-Z]{2,3}\d{3,4}$", "format": "ABC123", "example": "ABC123"},
    "Idaho": {"pattern": r"^[A-Z]{2,3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Illinois": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Indiana": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Iowa": {"pattern": r"^\d{3}[A-Z]{3}$", "format": "123ABC", "example": "123ABC"},
    "Kansas": {"pattern": r"^[A-Z]{3}\d{3}$", "format": "ABC123", "example": "ABC123"},
    "Kentucky": {"pattern": r"^[A-Z]{2,3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Louisiana": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Maine": {"pattern": r"^\d{4}[A-Z]{2}$", "format": "1234AB", "example": "1234AB"},
    "Maryland": {"pattern": r"^[A-Z]{2}\d{5}$", "format": "AB12345", "example": "AB12345"},
    "Massachusetts": {"pattern": r"^[A-Z]\d{2,3}[A-Z]{4}$", "format": "A12BCD", "example": "A12BCD"},
    "Michigan": {"pattern": r"^[A-Z]{3,4}\d{4}$", "format": "ABCD1234", "example": "ABCD1234"},
    "Minnesota": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Mississippi": {"pattern": r"^\d{3}[A-Z]{3}$", "format": "123ABC", "example": "123ABC"},
    "Missouri": {"pattern": r"[A-Z]\d{2}[A-Z]\d{2}[A-Z]$", "format": "A12B12C", "example": "A12B12C"},
    "Montana": {"pattern": r"^[A-Z]{2,3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Nebraska": {"pattern": r"^[A-Z]{2,3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Nevada": {"pattern": r"^\d{3}[A-Z]{3}$", "format": "123ABC", "example": "123ABC"},
    "New Hampshire": {"pattern": r"^[A-Z]{2,3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "New Jersey": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "New Mexico": {"pattern": r"^\d{3}[A-Z]{3}$", "format": "123ABC", "example": "123ABC"},
    "New York": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "North Carolina": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "North Dakota": {"pattern": r"^\d{3}[A-Z]{3}$", "format": "123ABC", "example": "123ABC"},
    "Ohio": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Oklahoma": {"pattern": r"^[A-Z]{3}\d{3}$", "format": "ABC123", "example": "ABC123"},
    "Oregon": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Pennsylvania": {"pattern": r"^\d{5,6}$", "format": "123456", "example": "123456"},
    "Rhode Island": {"pattern": r"^\d{5,6}$", "format": "123456", "example": "123456"},
    "South Carolina": {"pattern": r"^\d{5,6}$", "format": "123456", "example": "123456"},
    "South Dakota": {"pattern": r"^\d{5,6}$", "format": "123456", "example": "123456"},
    "Tennessee": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Texas": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Utah": {"pattern": r"^[A-Z]{3}\d{3,4}$", "format": "ABC123", "example": "ABC123"},
    "Vermont": {"pattern": r"^\d{4}[A-Z]{2}$", "format": "1234AB", "example": "1234AB"},
    "Virginia": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Washington": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "West Virginia": {"pattern": r"^[A-Z]{2,3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Wisconsin": {"pattern": r"^\d{4}[A-Z]{2}$", "format": "1234AB", "example": "1234AB"},
    "Wyoming": {"pattern": r"^\d{5,6}$", "format": "123456", "example": "123456"},
    "Ontario": {"pattern": r"^[A-Z]{4}\d{3}$", "format": "ABCD123", "example": "ABCD123"},
    "British Columbia": {"pattern": r"^[A-Z]{4}\d{2}[A-Z]$", "format": "ABCD12E", "example": "ABCD12E"},
    "Alberta": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Quebec": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Manitoba": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "Saskatchewan": {"pattern": r"^[A-Z]{3}\d{4}$", "format": "ABC1234", "example": "ABC1234"},
    "NSW": {"pattern": r"^[A-Z]{2}-[A-Z]{2}-\d{2}$", "format": "AA-AA-12", "example": "AB-CD-12"},
    "Victoria": {"pattern": r"^[A-Z]{3}-\d{3}$", "format": "ABC-123", "example": "ABC-123"},
    "Queensland": {"pattern": r"^\d{3}[A-Z]{3}$", "format": "123ABC", "example": "123ABC"},
    "South Australia": {"pattern": r"^[A-Z]{2}[A-Z0-9]{4}$", "format": "AB123C", "example": "AB123C"},
    "Western Australia": {"pattern": r"^[A-Z]{3}\d{3}$", "format": "ABC123", "example": "ABC123"},
    "Northern Territory": {"pattern": r"^[A-Z]{2}[A-Z0-9]{4}$", "format": "AB123C", "example": "AB123C"},
    "Tasmania": {"pattern": r"^[A-Z]{3}\d{3}$", "format": "ABC123", "example": "ABC123"},
    "ACT": {"pattern": r"^[A-Z]{2}[A-Z0-9]{4}$", "format": "AB123C", "example": "AB123C"},
}

# ═══════════════════════════════════════════════════════════════
#  VIN MANUFACTURER DATA (WMI 3-character codes)
# ═══════════════════════════════════════════════════════════════

VIN_MANUFACTURERS = {
    "1FA-1FT": "Ford", "1G1-1GC": "Chevrolet", "1G6-1GN": "General Motors",
    "1HG": "Honda", "1J4-1J8": "Jeep", "1ME": "Mercury", "1N4-1NX": "Nissan",
    "1VW": "Volkswagen", "1ZV": "Ford", "2FA": "Ford Canada", "2G1": "Chevrolet Canada",
    "2HG": "Honda Canada", "2T1": "Toyota Canada", "3FA": "Ford Mexico",
    "3G1": "Chevrolet Mexico", "3VW": "Volkswagen Mexico", "4T1-4T4": "Toyota",
    "5FN-5J6": "Honda", "5NP": "Hyundai", "JDA": "Daihatsu", "JF1-JF2": "Subaru",
    "JH": "Honda", "JK": "Kawasaki", "JL": "Suzuki", "JM": "Mazda",
    "JN": "Nissan", "JS": "Suzuki", "JT": "Toyota", "JY": "Yamaha",
    "KL": "Daewoo", "KMH": "Hyundai", "KNA-KNJ": "Kia", "KNM": "SsangYong",
    "LA6": "Mitsubishi", "LBV": "BMW", "LDC": "Citroen", "LDN": "Nissan",
    "LFV": "Volkswagen", "LGB": "Nissan", "LJC": "JAC", "LL0": "Lifan",
    "LMG": "Great Wall", "LPA": "Peugeot", "LPS": "SAIC", "LTV": "Toyota",
    "LVG": "Toyota", "LVR": "Ford", "LVS": "Suzuki", "LVV": "Chery",
    "LZW": "SAIC-GM-Wuling", "MA1": "Mahindra", "MA3": "Maruti Suzuki",
    "MA6": "Renault Nissan", "MB8": "Tata", "MCA": "Fiat", "MHB": "Mercedes-Benz",
    "NLA": "Mercedes-Benz", "NLF": "Fiat", "NLH": "Hyundai", "NLT": "Tesla",
    "SAJ": "Jaguar", "SAL": "Land Rover", "SAV": "BMW", "SAZ": "Rolls-Royce",
    "SCC": "Lotus", "SCF": "Aston Martin", "SCM": "MG Rover", "SDB": "Nissan",
    "SFP": "Aston Martin", "SFZ": "Aston Martin", "SJJ": "Jaguar Land Rover",
    "TRU": "Audi", "TSE": "Skoda", "TSM": "Skoda", "TTV": "Suzuki",
    "WAU": "Audi", "WBA-WBY": "BMW", "WDB-WDZ": "Mercedes-Benz",
    "WP0": "Porsche", "WVW": "Volkswagen", "WV1-WV3": "Volkswagen Commercial",
    "ZAM": "Maserati", "ZAP-ZAR": "Alfa Romeo", "ZFF": "Ferrari",
    "ZLA": "Lamborghini",
}

# ═══════════════════════════════════════════════════════════════
#  PUBLIC VEHICLE DATA SOURCES
# ═══════════════════════════════════════════════════════════════

VEHICLE_SOURCES = {
    "NHTSA VIN Decoder": {
        "url": "https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json",
        "type": "free_api",
        "description": "Official US government VIN decoder",
    },
    "NHTSA Recalls": {
        "url": "https://api.nhtsa.gov/recalls/recallsByVehicle?make={make}&model={model}&modelYear={year}",
        "type": "free_api",
        "description": "US government recall database",
    },
    "Edmunds": {
        "url": "https://www.edmunds.com/gateway/api/purchasefunnel/v1/srp/inventory?vin={vin}",
        "type": "free_api",
        "description": "Vehicle pricing and inventory",
    },
    "KBB": {
        "url": "https://www.kbb.com/",
        "type": "web",
        "description": "Kelley Blue Book vehicle valuation",
    },
    "AutoCheck": {
        "url": "https://www.autocheck.com/vehiclehistory/?vin={vin}",
        "type": "paid",
        "description": "Vehicle history reports (Experian)",
    },
    "CARFAX": {
        "url": "https://www.carfax.com/VehicleHistory/p/Report.cfx?vin={vin}",
        "type": "paid",
        "description": "Vehicle history reports",
    },
    "NMVTIS": {
        "url": "https://www.nmvtis.gov/",
        "type": "government",
        "description": "National Motor Vehicle Title Information System",
    },
    "NICB VINCheck": {
        "url": "https://www.nicb.org/vincheck",
        "type": "free",
        "description": "Stolen vehicle check (National Insurance Crime Bureau)",
    },
    "NICB TotalLoss": {
        "url": "https://www.nicb.org/theft-and-fraud-vehicles/total-loss-vin",
        "type": "free",
        "description": "Total loss vehicle check",
    },
    "VehicleHistory": {
        "url": "https://www.vehiclehistory.com/vin-report/{vin}",
        "type": "free",
        "description": "Free vehicle history reports",
    },
    "VIN Decoders": {
        "url": "https://www.vindecoderz.com/EN/check-lookup/{vin}",
        "type": "free",
        "description": "VIN decoding and lookup",
    },
    "EPA Fuel Economy": {
        "url": "https://www.fueleconomy.gov/feg/noframes/{vin}.shtml",
        "type": "free",
        "description": "Fuel economy data by VIN",
    },
    "TitleCheck": {
        "url": "https://www.titlecheck.com/",
        "type": "paid",
        "description": "Title history and salvage records",
    },
    "VinAudit": {
        "url": "https://www.vinaudit.com/vin/{vin}",
        "type": "paid",
        "description": "Vehicle history and title records",
    },
    "Bumper": {
        "url": "https://www.bumper.com/vin/{vin}",
        "type": "free",
        "description": "Vehicle recall and specs data",
    },
    "SpotCheck": {
        "url": "https://www.spotcheck.uk/",
        "type": "paid",
        "description": "UK vehicle check (MOT, tax, etc.)",
    },
    "Gov.uk MOT": {
        "url": "https://www.gov.uk/check-vehicle-tax",
        "type": "free",
        "description": "UK government vehicle tax check",
    },
    "Gov.uk MOT History": {
        "url": "https://www.check-mot.service.gov.uk/",
        "type": "free",
        "description": "UK government MOT history",
    },
    "DVLA": {
        "url": "https://www.gov.uk/check-vehicle-tax",
        "type": "free",
        "description": "UK DVLA vehicle tax check",
    },
    "CarVertical": {
        "url": "https://www.carvertical.com/",
        "type": "paid",
        "description": "Blockchain-based vehicle history",
    },
    "AutoDNA": {
        "url": "https://www.autodna.com/vin/{vin}",
        "type": "paid",
        "description": "European vehicle history",
    },
    "AutoCataliza": {
        "url": "https://www.autocataliza.fr/",
        "type": "paid",
        "description": "French vehicle history",
    },
    "DATEN": {
        "url": "https://www.daten.de/",
        "type": "paid",
        "description": "German vehicle data",
    },
    "CEPIA": {
        "url": "https://www.cepiA.com/",
        "type": "paid",
        "description": "Italian vehicle history",
    },
    "RACV": {
        "url": "https://www.racv.com.au/",
        "type": "paid",
        "description": "Australian vehicle history",
    },
    "CarCheck": {
        "url": "https://www.carcheck.co.nz/",
        "type": "paid",
        "description": "New Zealand vehicle check",
    },
    "RTA": {
        "url": "https://www.rta.nsw.gov.au/",
        "type": "free",
        "description": "NSW Roads and Traffic Authority",
    },
    "Vicroads": {
        "url": "https://www.vicroads.vic.gov.au/",
        "type": "free",
        "description": "Victoria Roads (Australia)",
    },
    "Transport NSW": {
        "url": "https://transportnsw.info/",
        "type": "free",
        "description": "Transport for NSW vehicle registration",
    },
    "QLD Transport": {
        "url": "https://www.tmr.qld.gov.au/",
        "type": "free",
        "description": "Queensland transport vehicle registration",
    },
    "SA Transport": {
        "url": "https://www.sa.gov.au/topics/driving-and-transport",
        "type": "free",
        "description": "South Australia transport vehicle registration",
    },
    "WA Transport": {
        "url": "https://www.transport.wa.gov.au/",
        "type": "free",
        "description": "Western Australia transport vehicle registration",
    },
    "NT Transport": {
        "url": "https://nt.gov.au/driving/vehicle-registration",
        "type": "free",
        "description": "Northern Territory vehicle registration",
    },
    "Tasmania Transport": {
        "url": "https://www.transport.tas.gov.au/",
        "type": "free",
        "description": "Tasmania vehicle registration",
    },
    "ACT Transport": {
        "url": "https://www.accesscanberra.act.gov.au/",
        "type": "free",
        "description": "ACT vehicle registration",
    },
    "ICBC": {
        "url": "https://www.icbc.com/",
        "type": "free",
        "description": "Insurance Corporation of British Columbia",
    },
    "SAAQ": {
        "url": "https://www.saaq.gouv.qc.ca/",
        "type": "free",
        "description": "Societe de l'assurance automobile du Quebec",
    },
    "MTO": {
        "url": "https://www.ontario.ca/page/driving-and-roads",
        "type": "free",
        "description": "Ontario Ministry of Transportation",
    },
    "MTO": {
        "url": "https://www.ontario.ca/page/driving-and-roads",
        "type": "free",
        "description": "Ontario Ministry of Transportation",
    },
}

# ═══════════════════════════════════════════════════════════════
#  OSINT TOOLS FOR VEHICLE INVESTIGATION
# ═══════════════════════════════════════════════════════════════

OSINT_TOOLS = {
    "Sherlock": {
        "url": "https://github.com/sherlock-project/sherlock",
        "description": "Username OSINT across 400+ platforms",
        "use_case": "Find social media linked to owner",
    },
    "Recon-ng": {
        "url": "https://github.com/lanmaster53/recon-ng",
        "description": "Full-featured reconnaissance framework",
        "use_case": "Domain/IP recon on vehicle websites",
    },
    "Maltego": {
        "url": "https://www.maltego.com/",
        "description": "Link analysis and data mining",
        "use_case": "Connect vehicle to owner through data relationships",
    },
    "SpiderFoot": {
        "url": "https://www.spiderfoot.net/",
        "description": "OSINT automation tool",
        "use_case": "Automated recon on vehicle owner",
    },
    "theHarvester": {
        "url": "https://github.com/laramies/theHarvester",
        "description": "Email/subdomain/IP harvester",
        "use_case": "Gather emails associated with vehicle registration",
    },
    "OSINT Framework": {
        "url": "https://osintframework.com/",
        "description": "Collection of OSINT tools",
        "use_case": "General OSINT for vehicle investigations",
    },
    "ExifTool": {
        "url": "https://exiftool.org/",
        "description": "Metadata reader/writer",
        "use_case": "Extract GPS data from vehicle photos",
    },
    "Google Earth Pro": {
        "url": "https://earth.google.com/web/",
        "description": "Satellite imagery",
        "use_case": "Locate vehicle through satellite imagery",
    },
    "Wayback Machine": {
        "url": "https://web.archive.org/",
        "description": "Website archive",
        "use_case": "Historical vehicle listings and seller info",
    },
    "TinEye": {
        "url": "https://tineye.com/",
        "description": "Reverse image search",
        "use_case": "Find vehicle photos across the web",
    },
    "Google Lens": {
        "url": "https://lens.google.com/",
        "description": "Visual search",
        "use_case": "Identify vehicle from photos",
    },
}


def banner():
    console.clear()
    for l in ASCII:
        console.print(f"[bold cyan]{l}[/bold cyan]", justify="center")
    console.print()
    console.print("[bold white]  License Plate OSINT · Vehicle History · VIN Decoder[/bold white]", justify="center")
    console.print("[bold red]  Made by b0dj0x · https://b0dj0x.cc[/bold red]\n")


class CarIntel:
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.s = requests.Session()
        self.s.headers["User-Agent"] = UA
        self.s.verify = False
        self.results = {}

    # ═══════════════════════════════════════════
    #  1. VIN DECODE
    # ═══════════════════════════════════════════

    def decode_vin(self, vin):
        """Decode VIN locally using WMI and year codes"""
        vin = vin.upper().strip()
        if len(vin) != 17:
            console.print(f"[red]  Invalid VIN: must be 17 characters (got {len(vin)})[/red]")
            return None

        # Check for forbidden characters (I, O, Q)
        if re.search(r"[IOQ]", vin):
            console.print(f"[red]  Invalid VIN: contains forbidden characters (I, O, Q)[/red]")
            return None

        result = {
            "vin": vin,
            "wmi": vin[:3],
            "vds": vin[3:9],
            "vis": vin[9:],
            "manufacturer": "Unknown",
            "country": "Unknown",
            "year": None,
            "assembly_plant": vin[10],
            "sequence_number": vin[11:17],
        }

        # Decode WMI (World Manufacturer Identifier)
        wmi = vin[:3]
        for prefix, manufacturer in VIN_WMI.items():
            if wmi.startswith(prefix) or wmi == prefix:
                result["manufacturer"] = manufacturer
                break

        # Decode country
        country_codes = {
            "1": "United States", "2": "Canada", "3": "Mexico",
            "4": "United States", "5": "United States",
            "J": "Japan", "K": "South Korea", "L": "China",
            "M": "India", "S": "United Kingdom", "T": "Czech Republic",
            "V": "France/Germany", "W": "Germany", "Z": "Italy",
        }
        result["country"] = country_codes.get(wmi[0], "Unknown")

        # Decode year (position 10)
        year_char = vin[9]
        year = VIN_YEAR.get(year_char) or VIN_YEAR_OLD.get(year_char)
        result["year"] = year

        # Decode engine type (position 8 - rough guess based on common codes)
        engine_codes = {
            "A": "1.8L", "B": "2.0L", "C": "2.2L", "D": "2.4L",
            "E": "2.5L", "F": "3.0L", "G": "3.2L", "H": "3.5L",
            "J": "3.8L", "K": "4.0L", "L": "4.2L", "M": "4.6L",
            "N": "5.0L", "P": "5.4L", "R": "5.7L", "S": "6.0L",
            "T": "6.2L", "U": "6.5L", "V": "8.0L",
        }
        result["engine_guess"] = engine_codes.get(vin[7], "Unknown")

        return result

    def vin_lookup(self, vin):
        """Look up VIN via NHTSA API"""
        console.print(f"[bold cyan]  VIN Lookup: {vin}[/bold cyan]\n")

        # Local decode first
        local = self.decode_vin(vin)
        if local:
            console.print(f"  [yellow]Local Decode:[/yellow]")
            console.print(f"    VIN: {local['vin']}")
            console.print(f"    Manufacturer: {local['manufacturer']}")
            console.print(f"    Country: {local['country']}")
            console.print(f"    Year: {local['year'] or 'Unknown'}")
            console.print(f"    WMI: {local['wmi']}")
            console.print(f"    Engine (guess): {local['engine_guess']}")
            console.print()

        # NHTSA API
        console.print(f"  [yellow]NHTSA API:[/yellow]")
        try:
            resp = self.s.get(
                f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json",
                timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("Results", [])

                # Extract key info
                key_fields = {
                    "Make": "Make",
                    "Model": "Model",
                    "ModelYear": "Model Year",
                    "BodyClass": "Body Class",
                    "DisplacementL": "Engine Displacement (L)",
                    "DisplacementCC": "Engine Displacement (CC)",
                    "EngineCylinders": "Cylinders",
                    "EngineHP": "Horsepower",
                    "FuelTypePrimary": "Fuel Type",
                    "TransmissionStyle": "Transmission",
                    "DriveType": "Drive Type",
                    "PlantCity": "Assembly City",
                    "PlantState": "Assembly State",
                    "PlantCountry": "Assembly Country",
                    "Manufacturer": "Manufacturer",
                    "Trim": "Trim",
                    "Doors": "Doors",
                    "Windows": "Windows",
                    "SteeringType": "Steering",
                    "ABS": "ABS",
                    "AirBagLocCurtain": "Curtain Airbags",
                    "AirBagLocFront": "Front Airbags",
                    "AirBagLocSide": "Side Airbags",
                    "SeatBeltsAll": "Seat Belts",
                    "BackupCamera": "Backup Camera",
                    "BlindSpotMon": "Blind Spot Monitor",
                    "LaneAssist": "Lane Assist",
                    "ForwardCollisionWarning": "Forward Collision Warning",
                    "LaneDepartureWarning": "Lane Departure Warning",
                    "ParkingAssist": "Parking Assist",
                    "TractionControl": "Traction Control",
                    "StabilityControl": "Stability Control",
                    "Turbo": "Turbo",
                    "ValveTrainDesign": "Valve Train",
                    "EngineConfiguration": "Engine Config",
                    "FuelInjectionType": "Fuel Injection",
                    "CylinderHeadType": "Head Type",
                    "DisplacementCC": "Displacement (CC)",
                    "EngineCylinders": "Cylinders",
                    "OtherEngineInfo": "Engine Info",
                    "ErrorCode": "Error Code",
                    "ErrorText": "Error Text",
                    "AdditionalErrorText": "Additional Error",
                }

                found = False
                for item in results:
                    variable = item.get("Variable", "")
                    value = item.get("Value", "")
                    if variable in key_fields and value and value != "Not Applicable" and value != "" and value != "0":
                        console.print(f"    {key_fields[variable]}: [green]{value}[/green]")
                        found = True

                if not found:
                    console.print(f"    [dim]No detailed data found from NHTSA[/dim]")

                self.results["vin_nhtsa"] = data
            else:
                console.print(f"    [dim]NHTSA API error: {resp.status_code}[/dim]")
        except:
            console.print(f"    [dim]NHTSA API connection failed[/dim]")

        # Generate OSINT links
        console.print()
        console.print(f"  [bold cyan]  OSINT Links[/bold cyan]\n")
        links = [
            ("NHTSA VIN Decoder", f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"),
            ("NHTSA Recalls", f"https://www.nhtsa.gov/recalls#vin={vin}"),
            ("NICB VINCheck", f"https://www.nicb.org/vincheck"),
            ("NICB TotalLoss", f"https://www.nicb.org/theft-and-fraud-vehicles/total-loss-vin"),
            ("CARFAX", f"https://www.carfax.com/VehicleHistory/p/Report.cfx?vin={vin}"),
            ("AutoCheck", f"https://www.autocheck.com/vehiclehistory/?vin={vin}"),
            ("Edmunds", f"https://www.edmunds.com/vin-decoder/?vin={vin}"),
            ("KBB", f"https://www.kbb.com/whats-my-car-worth/vin/{vin}"),
            ("VehicleHistory", f"https://www.vehiclehistory.com/vin-report/{vin}"),
            ("VinAudit", f"https://www.vinaudit.com/vin/{vin}"),
            ("Bumper", f"https://www.bumper.com/vin/{vin}"),
            ("EPA Fuel Economy", f"https://www.fueleconomy.gov/feg/noframes/{vin}.shtml"),
            ("VIN Decoders", f"https://www.vindecoderz.com/EN/check-lookup/{vin}"),
            ("TitleCheck", f"https://www.titlecheck.com/"),
            ("CarVertical", f"https://www.carvertical.com/"),
            ("AutoDNA", f"https://www.autodna.com/vin/{vin}"),
            ("Gov.uk MOT", f"https://www.check-mot.service.gov.uk/"),
            ("DVLA", f"https://www.gov.uk/check-vehicle-tax"),
            ("Gov.uk MOT History", f"https://www.check-mot.service.gov.uk/results?registration={vin}"),
            ("SpotCheck", f"https://www.spotcheck.uk/"),
            ("RACV", f"https://www.racv.com.au/"),
            ("CarCheck", f"https://www.carcheck.co.nz/"),
            ("RTA NSW", f"https://www.service.nsw.gov.au/transaction/check-vehicle-registration"),
            ("Vicroads", f"https://www.vicroads.vic.gov.au/"),
            ("QLD Transport", f"https://www.tmr.qld.gov.au/"),
            ("SA Transport", f"https://www.sa.gov.au/topics/driving-and-transport"),
            ("WA Transport", f"https://www.transport.wa.gov.au/"),
            ("NT Transport", f"https://nt.gov.au/driving/vehicle-registration"),
            ("Tasmania Transport", f"https://www.transport.tas.gov.au/"),
            ("ACT Transport", f"https://www.accesscanberra.act.gov.au/"),
            ("ICBC", f"https://www.icbc.com/"),
            ("SAAQ", f"https://www.saaq.gouv.qc.ca/"),
            ("MTO Ontario", f"https://www.ontario.ca/page/driving-and-roads"),
            ("Google", f"https://www.google.com/search?q=%22{vin}%22"),
            ("GitHub", f"https://github.com/search?q={vin}&type=code"),
        ]

        for i, (name, url) in enumerate(links, 1):
            console.print(f"    [green]{i:2d}.[/green] [bold white]{name}[/bold white]")
            console.print(f"        {url}")

    # ═══════════════════════════════════════════
    #  2. LICENSE PLATE LOOKUP
    # ═══════════════════════════════════════════

    def plate_lookup(self, plate, state=None):
        """Look up license plate"""
        console.print(f"[bold cyan]  License Plate Lookup: {plate}[/bold cyan]\n")

        plate = plate.upper().strip()

        # Identify state
        detected_state = None
        if state:
            detected_state = state
        else:
            for st, fmt in PLATE_FORMATS.items():
                if re.match(fmt["pattern"], plate):
                    detected_state = st
                    break

        if detected_state:
            console.print(f"  [green]Detected State/Region: {detected_state}[/green]\n")

        # Generate OSINT links
        console.print("[bold cyan]  OSINT Links[/bold cyan]\n")
        links = [
            ("NICB VINCheck", "https://www.nicb.org/vincheck"),
            ("NICB TotalLoss", "https://www.nicb.org/theft-and-fraud-vehicles/total-loss-vin"),
            ("CARFAX", "https://www.carfax.com/"),
            ("AutoCheck", "https://www.autocheck.com/"),
            ("VehicleHistory", "https://www.vehiclehistory.com/"),
            ("Gov.uk MOT", "https://www.check-mot.service.gov.uk/"),
            ("DVLA", "https://www.gov.uk/check-vehicle-tax"),
            ("Gov.uk MOT History", "https://www.check-mot.service.gov.uk/"),
            ("SpotCheck", "https://www.spotcheck.uk/"),
            ("RTA NSW", "https://www.service.nsw.gov.au/transaction/check-vehicle-registration"),
            ("Vicroads", "https://www.vicroads.vic.gov.au/"),
            ("QLD Transport", "https://www.tmr.qld.gov.au/"),
            ("SA Transport", "https://www.sa.gov.au/topics/driving-and-transport"),
            ("WA Transport", "https://www.transport.wa.gov.au/"),
            ("NT Transport", "https://nt.gov.au/driving/vehicle-registration"),
            ("Tasmania Transport", "https://www.transport.tas.gov.au/"),
            ("ACT Transport", "https://www.accesscanberra.act.gov.au/"),
            ("ICBC", "https://www.icbc.com/"),
            ("SAAQ", "https://www.saaq.gouv.qc.ca/"),
            ("MTO Ontario", "https://www.ontario.ca/page/driving-and-roads"),
            ("CarVertical", "https://www.carvertical.com/"),
            ("AutoDNA", "https://www.autodna.com/"),
            ("TitleCheck", "https://www.titlecheck.com/"),
            ("VinAudit", "https://www.vinaudit.com/"),
            ("Bumper", "https://www.bumper.com/"),
            ("Edmunds", "https://www.edmunds.com/"),
            ("KBB", "https://www.kbb.com/"),
            ("RACV", "https://www.racv.com.au/"),
            ("CarCheck", "https://www.carcheck.co.nz/"),
            ("Google", f"https://www.google.com/search?q=%22{plate}%22+vehicle"),
            ("Google Images", f"https://www.google.com/search?q=%22{plate}%22&tbm=isch"),
            ("TinEye", "https://tineye.com/"),
            ("Google Lens", "https://lens.google.com/"),
            ("Wayback Machine", f"https://web.archive.org/web/*/{plate}"),
            ("GitHub", f"https://github.com/search?q={plate}&type=code"),
        ]

        for i, (name, url) in enumerate(links, 1):
            console.print(f"  [green]{i:2d}.[/green] [bold white]{name}[/bold white]")
            console.print(f"      {url}")

        # Plate format info
        if detected_state and detected_state in PLATE_FORMATS:
            fmt = PLATE_FORMATS[detected_state]
            console.print()
            console.print(f"  [yellow]Plate Format for {detected_state}:[/yellow]")
            console.print(f"    Format: {fmt['format']}")
            console.print(f"    Example: {fmt['example']}")

    # ═══════════════════════════════════════════
    #  3. RECALL CHECK
    # ═══════════════════════════════════════════

    def recall_check(self, make, model, year):
        """Check for vehicle recalls"""
        console.print(f"[bold cyan]  Recall Check: {year} {make} {model}[/bold cyan]\n")

        try:
            resp = self.s.get(
                f"https://api.nhtsa.gov/recalls/recallsByVehicle?make={make}&model={model}&modelYear={year}",
                timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                recalls = data.get("results", [])

                if recalls:
                    console.print(f"  [red]Found {len(recalls)} recalls:[/red]\n")
                    for i, recall in enumerate(recalls, 1):
                        console.print(f"  [yellow]{i}. Recall #{recall.get('NHTSACampaignNumber', 'Unknown')}[/yellow]")
                        console.print(f"    Component: {recall.get('Component', 'Unknown')}")
                        console.print(f"    Consequence: {recall.get('Consequence', 'Unknown')[:100]}")
                        console.print(f"    Remedy: {recall.get('Remedy', 'Unknown')[:100]}")
                        console.print()
                else:
                    console.print(f"  [green]No recalls found for {year} {make} {model}[/green]")
            else:
                console.print(f"  [dim]NHTSA API error: {resp.status_code}[/dim]")
        except:
            console.print(f"  [dim]NHTSA API connection failed[/dim]")

    # ═══════════════════════════════════════════
    #  4. VEHICLE HISTORY SOURCES
    # ═══════════════════════════════════════════

    def vehicle_history(self, vin):
        """Show vehicle history sources"""
        console.print(f"[bold cyan]  Vehicle History Sources: {vin}[/bold cyan]\n")

        for name, info in VEHICLE_SOURCES.items():
            free_tag = "[green]FREE[/green]" if info["type"] in ("free", "free_api", "government") else "[red]PAID[/red]"
            url = info["url"].format(vin=vin, make="", model="", year="")
            console.print(f"  [bold white]{name}[/bold white] {free_tag} [dim]— {info['description']}[/dim]")
            console.print(f"    {url}")

    # ═══════════════════════════════════════════
    #  5. STOLEN VEHICLE CHECK
    # ═══════════════════════════════════════════

    def stolen_check(self, vin):
        """Check if vehicle is stolen"""
        console.print(f"[bold cyan]  Stolen Vehicle Check: {vin}[/bold cyan]\n")

        console.print("[yellow]  Checking NICB databases...[/yellow]\n")

        # NICB VINCheck
        try:
            resp = self.s.get(
                f"https://www.nicb.org/vincheck",
                timeout=self.timeout)
            console.print(f"  [green]✓[/green] NICB VINCheck: https://www.nicb.org/vincheck")
            console.print(f"    [dim]Enter VIN to check for theft/total loss records[/dim]")
        except:
            console.print(f"  [dim]✗ NICB: Connection failed[/dim]")

        # NICB TotalLoss
        try:
            resp = self.s.get(
                f"https://www.nicb.org/theft-and-fraud-vehicles/total-loss-vin",
                timeout=self.timeout)
            console.print(f"  [green]✓[/green] NICB TotalLoss: https://www.nicb.org/theft-and-fraud-vehicles/total-loss-vin")
            console.print(f"    [dim]Check if vehicle has total loss/salvage record[/dim]")
        except:
            console.print(f"  [dim]✗ NICB TotalLoss: Connection failed[/dim]")

        # Generate OSINT links
        console.print()
        console.print("[bold cyan]  Additional OSINT Links[/bold cyan]\n")
        links = [
            ("Google", f"https://www.google.com/search?q=%22{vin}%22+stolen"),
            ("CarVertical", "https://www.carvertical.com/"),
            ("AutoDNA", f"https://www.autodna.com/vin/{vin}"),
            ("TitleCheck", "https://www.titlecheck.com/"),
            ("VinAudit", f"https://www.vinaudit.com/vin/{vin}"),
            ("Bumper", f"https://www.bumper.com/vin/{vin}"),
            ("SpotCheck", "https://www.spotcheck.uk/"),
            ("Gov.uk MOT", "https://www.check-mot.service.gov.uk/"),
            ("DVLA", "https://www.gov.uk/check-vehicle-tax"),
            ("ICBC", "https://www.icbc.com/"),
            ("SAAQ", "https://www.saaq.gouv.qc.ca/"),
            ("MTO Ontario", "https://www.ontario.ca/page/driving-and-roads"),
            ("RTA NSW", "https://www.service.nsw.gov.au/transaction/check-vehicle-registration"),
            ("Vicroads", "https://www.vicroads.vic.gov.au/"),
            ("QLD Transport", "https://www.tmr.qld.gov.au/"),
            ("SA Transport", "https://www.sa.gov.au/topics/driving-and-transport"),
            ("WA Transport", "https://www.transport.wa.gov.au/"),
            ("NT Transport", "https://nt.gov.au/driving/vehicle-registration"),
            ("Tasmania Transport", "https://www.transport.tas.gov.au/"),
            ("ACT Transport", "https://www.accesscanberra.act.gov.au/"),
        ]

        for i, (name, url) in enumerate(links, 1):
            console.print(f"  [green]{i:2d}.[/green] [bold white]{name}[/bold white]")
            console.print(f"      {url}")

    # ═══════════════════════════════════════════
    #  6. STATE PLATE FORMATS
    # ═══════════════════════════════════════════

    def plate_formats(self):
        """Show all US/Canada/Australia plate formats"""
        console.print("[bold cyan]  License Plate Formats by State/Region[/bold cyan]\n")

        table = Table(box=box.ROUNDED, show_lines=True)
        table.add_column("State/Region", style="green", width=20)
        table.add_column("Format", style="yellow", width=15)
        table.add_column("Pattern", style="dim", width=20)
        table.add_column("Example", style="cyan", width=12)

        for state, fmt in PLATE_FORMATS.items():
            table.add_row(state, fmt["format"], fmt["pattern"], fmt["example"])

        console.print(table)

    # ═══════════════════════════════════════════
    #  7. OSINT TOOLS
    # ═══════════════════════════════════════════

    def osint_tools(self):
        """Show OSINT tools for vehicle investigation"""
        console.print("[bold cyan]  OSINT Tools for Vehicle Investigation[/bold cyan]\n")

        for name, info in OSINT_TOOLS.items():
            console.print(f"  [bold white]{name}[/bold white] [dim]— {info['description']}[/dim]")
            console.print(f"    Use case: {info['use_case']}")
            console.print(f"    {info['url']}")
            console.print()


def main():
    p = argparse.ArgumentParser(
        prog="carintel",
        description="CarIntel — License Plate OSINT · Vehicle History · VIN Decoder")
    sub = p.add_subparsers(dest="command", help="Command to execute")

    # VIN lookup
    vin_p = sub.add_parser("vin", help="Decode and look up VIN")
    vin_p.add_argument("vin", help="17-character VIN")

    # License plate lookup
    plate_p = sub.add_parser("plate", help="Look up license plate")
    plate_p.add_argument("number", help="License plate number")
    plate_p.add_argument("--state", help="State/region (optional)")

    # Recall check
    recall_p = sub.add_parser("recall", help="Check for vehicle recalls")
    recall_p.add_argument("make", help="Vehicle make (e.g., Toyota)")
    recall_p.add_argument("model", help="Vehicle model (e.g., Camry)")
    recall_p.add_argument("year", help="Vehicle year (e.g., 2023)")

    # Stolen check
    stolen_p = sub.add_parser("stolen", help="Check if vehicle is stolen")
    stolen_p.add_argument("vin", help="17-character VIN")

    # Vehicle history
    history_p = sub.add_parser("history", help="Show vehicle history sources")
    history_p.add_argument("vin", help="17-character VIN")

    # Plate formats
    sub.add_parser("formats", help="Show all plate formats by state/region")

    # OSINT tools
    sub.add_parser("tools", help="Show OSINT tools for vehicle investigation")

    args = p.parse_args()

    banner()

    ci = CarIntel()

    if args.command == "vin":
        ci.vin_lookup(args.vin)
    elif args.command == "plate":
        ci.plate_lookup(args.number, args.state)
    elif args.command == "recall":
        ci.recall_check(args.make, args.model, args.year)
    elif args.command == "stolen":
        ci.stolen_check(args.vin)
    elif args.command == "history":
        ci.vehicle_history(args.vin)
    elif args.command == "formats":
        ci.plate_formats()
    elif args.command == "tools":
        ci.osint_tools()
    else:
        p.print_help()

    console.print("\n[bold green]  Done.[/bold green]\n")


if __name__ == "__main__":
    main()
