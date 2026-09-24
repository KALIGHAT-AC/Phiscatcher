import sys
import os
import json
import math
import statistics
import joblib
from collections import Counter
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "phishing_model.pkl"
)


# ============================================================
# SETTINGS
# ============================================================

FLOW_TIMEOUT = 5.0


# ============================================================
# FEATURES USED BY THE TRAINED MODEL
# ============================================================

LIVE_FEATURES = [
    "duration",
    "packets_numbers",
    "receiving_packets_numbers",
    "sending_packets_numbers",
    "total_bytes",
    "receiving_bytes",
    "sending_bytes",
    "packets_rate",
    "packets_len_rate",

    "min_packets_len",
    "max_packets_len",
    "mean_packets_len",
    "median_packets_len",
    "mode_packets_len",

    "min_receiving_packets_len",
    "max_receiving_packets_len",
    "mean_receiving_packets_len",
    "median_receiving_packets_len",
    "mode_receiving_packets_len",

    "min_sending_packets_len",
    "max_sending_packets_len",
    "mean_sending_packets_len",
    "median_sending_packets_len",
    "mode_sending_packets_len",

    "dns_domain_name_length",
    "dns_subdomain_name_length",
    "dns_top_level_domain",
    "dns_second_level_domain",

    "character_entropy",
    "numerical_percentage",
    "max_continuous_alphabet_len",
    "max_continuous_consonants_len",
    "vowels_consonant_ratio",
    "conv_freq_vowels_consonants"
]


# ============================================================
# LOAD MODEL
# ============================================================

try:

    model = joblib.load(MODEL_PATH)

    print(
        "ML model loaded successfully.",
        flush=True
    )

except Exception as error:

    print(
        f"Failed to load ML model: {error}",
        file=sys.stderr,
        flush=True
    )

    sys.exit(1)


# ============================================================
# FLOW STORAGE
# ============================================================

flows = {}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_float(value, default=0.0):

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):

    try:
        return int(value)

    except (TypeError, ValueError):
        return default


def mode_value(values):

    if not values:
        return 0

    try:
        return statistics.mode(values)

    except statistics.StatisticsError:

        counter = Counter(values)

        return counter.most_common(1)[0][0]


def entropy(text):

    if not text:
        return 0.0

    counter = Counter(text)

    length = len(text)

    result = 0.0

    for count in counter.values():

        probability = count / length

        result -= probability * math.log2(
            probability
        )

    return result


def longest_alphabet_sequence(text):

    longest = 0
    current = 0

    for char in text:

        if char.isalpha():

            current += 1

            if current > longest:
                longest = current

        else:

            current = 0

    return longest


def longest_consonant_sequence(text):

    vowels = set("aeiou")

    longest = 0
    current = 0

    for char in text.lower():

        if char.isalpha() and char not in vowels:

            current += 1

            if current > longest:
                longest = current

        else:

            current = 0

    return longest


def calculate_domain_features(domain):

    if not domain:

        return {
            "dns_domain_name_length": 0,
            "dns_subdomain_name_length": 0,
            "dns_top_level_domain": "",
            "dns_second_level_domain": "",
            "character_entropy": 0.0,
            "numerical_percentage": 0.0,
            "max_continuous_alphabet_len": 0,
            "max_continuous_consonants_len": 0,
            "vowels_consonant_ratio": 0.0,
            "conv_freq_vowels_consonants": 0.0
        }

    domain = domain.lower().strip().rstrip(".")

    # --------------------------------------------------------
    # Domain length
    # --------------------------------------------------------

    domain_length = len(domain)

    parts = [
        part
        for part in domain.split(".")
        if part
    ]

    # --------------------------------------------------------
    # TLD
    # --------------------------------------------------------

    if len(parts) >= 1:
        tld = parts[-1]
    else:
        tld = ""

    # --------------------------------------------------------
    # Second-level domain
    # --------------------------------------------------------

    if len(parts) >= 2:
        second_level = parts[-2]
    else:
        second_level = ""

    # --------------------------------------------------------
    # Subdomain
    # Everything before second-level domain
    # --------------------------------------------------------

    if len(parts) > 2:

        subdomain_parts = parts[:-2]

        subdomain = ".".join(
            subdomain_parts
        )

    else:

        subdomain = ""

    # --------------------------------------------------------
    # Character statistics
    # --------------------------------------------------------

    characters = [
        char
        for char in domain
        if char.isalnum()
    ]

    if characters:

        numbers = sum(
            char.isdigit()
            for char in characters
        )

        numerical_percentage = (
            numbers / len(characters)
        ) * 100

    else:

        numerical_percentage = 0.0

    # --------------------------------------------------------
    # Vowels / consonants
    # --------------------------------------------------------

    vowels = set("aeiou")

    vowel_count = 0
    consonant_count = 0

    for char in domain.lower():

        if char.isalpha():

            if char in vowels:

                vowel_count += 1

            else:

                consonant_count += 1

    if consonant_count > 0:

        vowels_consonant_ratio = (
            vowel_count / consonant_count
        )

    else:

        vowels_consonant_ratio = 0.0

    total_letters = (
        vowel_count +
        consonant_count
    )

    if total_letters > 0:

        conv_freq_vowels_consonants = (
            abs(
                vowel_count -
                consonant_count
            ) / total_letters
        )

    else:

        conv_freq_vowels_consonants = 0.0

    return {

        "dns_domain_name_length":
            domain_length,

        "dns_subdomain_name_length":
            len(subdomain),

        "dns_top_level_domain":
            tld,

        "dns_second_level_domain":
            second_level,

        "character_entropy":
            entropy(domain),

        "numerical_percentage":
            numerical_percentage,

        "max_continuous_alphabet_len":
            longest_alphabet_sequence(
                domain
            ),

        "max_continuous_consonants_len":
            longest_consonant_sequence(
                domain
            ),

        "vowels_consonant_ratio":
            vowels_consonant_ratio,

        "conv_freq_vowels_consonants":
            conv_freq_vowels_consonants
    }


# ============================================================
# FLOW KEY
# ============================================================

def create_flow_key(packet):

    src_ip = packet.get("srcIp")
    dst_ip = packet.get("dstIp")

    src_port = packet.get("srcPort")
    dst_port = packet.get("dstPort")

    protocol = packet.get("protocol")

    if not src_ip or not dst_ip:

        return None

    # Convert both endpoints to comparable strings

    endpoint_a = (
        str(src_ip),
        safe_int(src_port, 0)
    )

    endpoint_b = (
        str(dst_ip),
        safe_int(dst_port, 0)
    )

    # Bidirectional flow

    if endpoint_a <= endpoint_b:

        first = endpoint_a
        second = endpoint_b

    else:

        first = endpoint_b
        second = endpoint_a

    return (
        first[0],
        first[1],
        second[0],
        second[1],
        str(protocol or "")
    )


# ============================================================
# CREATE NEW FLOW
# ============================================================

def create_flow(packet, timestamp):

    src_ip = packet.get("srcIp")
    dst_ip = packet.get("dstIp")

    flow = {

        # Original direction
        "src_ip": src_ip,
        "dst_ip": dst_ip,

        "src_port":
            safe_int(
                packet.get("srcPort"),
                0
            ),

        "dst_port":
            safe_int(
                packet.get("dstPort"),
                0
            ),

        "protocol":
            str(
                packet.get("protocol") or ""
            ),

        "start_time":
            timestamp,

        "last_time":
            timestamp,

        # All packet lengths
        "packet_lengths": [],

        # Sending direction
        "sending_packet_lengths": [],

        # Receiving direction
        "receiving_packet_lengths": [],

        "dns_domains": []
    }

    return flow


# ============================================================
# ADD PACKET TO FLOW
# ============================================================

def add_packet_to_flow(flow, packet, timestamp):

    packet_length = safe_int(
        packet.get("packetLength"),
        0
    )

    src_ip = packet.get("srcIp")
    dst_ip = packet.get("dstIp")

    # --------------------------------------------------------
    # Update timestamps
    # --------------------------------------------------------

    flow["last_time"] = timestamp

    # --------------------------------------------------------
    # Packet length
    # --------------------------------------------------------

    flow["packet_lengths"].append(
        packet_length
    )

    # --------------------------------------------------------
    # Direction
    # --------------------------------------------------------

    if src_ip == flow["src_ip"]:

        flow[
            "sending_packet_lengths"
        ].append(
            packet_length
        )

    elif src_ip == flow["dst_ip"]:

        flow[
            "receiving_packet_lengths"
        ].append(
            packet_length
        )

    # --------------------------------------------------------
    # DNS domain
    # --------------------------------------------------------

    dns_query = packet.get(
        "dnsQuery"
    )

    if dns_query:

        dns_query = (
            str(dns_query)
            .strip()
            .rstrip(".")
            .lower()
        )

        if dns_query:

            flow[
                "dns_domains"
            ].append(
                dns_query
            )


# ============================================================
# EXTRACT FEATURES
# ============================================================

def extract_features(flow):

    packet_lengths = flow[
        "packet_lengths"
    ]

    sending_lengths = flow[
        "sending_packet_lengths"
    ]

    receiving_lengths = flow[
        "receiving_packet_lengths"
    ]

    if not packet_lengths:

        return None

    # --------------------------------------------------------
    # Duration
    # --------------------------------------------------------

    duration = max(
        flow["last_time"] -
        flow["start_time"],
        0.0
    )

    # --------------------------------------------------------
    # Packet counts
    # --------------------------------------------------------

    packets_numbers = len(
        packet_lengths
    )

    sending_packets_numbers = len(
        sending_lengths
    )

    receiving_packets_numbers = len(
        receiving_lengths
    )

    # --------------------------------------------------------
    # Bytes
    # --------------------------------------------------------

    total_bytes = sum(
        packet_lengths
    )

    sending_bytes = sum(
        sending_lengths
    )

    receiving_bytes = sum(
        receiving_lengths
    )

    # --------------------------------------------------------
    # Rates
    #
    # Avoid division by zero.
    # --------------------------------------------------------

    rate_duration = max(
        duration,
        0.001
    )

    packets_rate = (
        packets_numbers /
        rate_duration
    )

    packets_len_rate = (
        total_bytes /
        rate_duration
    )

    # --------------------------------------------------------
    # Packet statistics
    # --------------------------------------------------------

    min_packets_len = min(
        packet_lengths
    )

    max_packets_len = max(
        packet_lengths
    )

    mean_packets_len = statistics.mean(
        packet_lengths
    )

    median_packets_len = statistics.median(
        packet_lengths
    )

    mode_packets_len = mode_value(
        packet_lengths
    )

    # --------------------------------------------------------
    # Receiving packet statistics
    # --------------------------------------------------------

    if receiving_lengths:

        min_receiving_packets_len = min(
            receiving_lengths
        )

        max_receiving_packets_len = max(
            receiving_lengths
        )

        mean_receiving_packets_len = (
            statistics.mean(
                receiving_lengths
            )
        )

        median_receiving_packets_len = (
            statistics.median(
                receiving_lengths
            )
        )

        mode_receiving_packets_len = (
            mode_value(
                receiving_lengths
            )
        )

    else:

        min_receiving_packets_len = 0
        max_receiving_packets_len = 0
        mean_receiving_packets_len = 0
        median_receiving_packets_len = 0
        mode_receiving_packets_len = 0

    # --------------------------------------------------------
    # Sending packet statistics
    # --------------------------------------------------------

    if sending_lengths:

        min_sending_packets_len = min(
            sending_lengths
        )

        max_sending_packets_len = max(
            sending_lengths
        )

        mean_sending_packets_len = (
            statistics.mean(
                sending_lengths
            )
        )

        median_sending_packets_len = (
            statistics.median(
                sending_lengths
            )
        )

        mode_sending_packets_len = (
            mode_value(
                sending_lengths
            )
        )

    else:

        min_sending_packets_len = 0
        max_sending_packets_len = 0
        mean_sending_packets_len = 0
        median_sending_packets_len = 0
        mode_sending_packets_len = 0

    # --------------------------------------------------------
    # DNS domain
    #
    # Use the latest DNS query seen in the flow.
    # --------------------------------------------------------

    if flow["dns_domains"]:

        domain = flow[
            "dns_domains"
        ][-1]

    else:

        domain = ""

    domain_features = (
        calculate_domain_features(
            domain
        )
    )

    # --------------------------------------------------------
    # Build final feature dictionary
    # --------------------------------------------------------

    features = {

        "duration":
            duration,

        "packets_numbers":
            packets_numbers,

        "receiving_packets_numbers":
            receiving_packets_numbers,

        "sending_packets_numbers":
            sending_packets_numbers,

        "total_bytes":
            total_bytes,

        "receiving_bytes":
            receiving_bytes,

        "sending_bytes":
            sending_bytes,

        "packets_rate":
            packets_rate,

        "packets_len_rate":
            packets_len_rate,

        "min_packets_len":
            min_packets_len,

        "max_packets_len":
            max_packets_len,

        "mean_packets_len":
            mean_packets_len,

        "median_packets_len":
            median_packets_len,

        "mode_packets_len":
            mode_packets_len,

        "min_receiving_packets_len":
            min_receiving_packets_len,

        "max_receiving_packets_len":
            max_receiving_packets_len,

        "mean_receiving_packets_len":
            mean_receiving_packets_len,

        "median_receiving_packets_len":
            median_receiving_packets_len,

        "mode_receiving_packets_len":
            mode_receiving_packets_len,

        "min_sending_packets_len":
            min_sending_packets_len,

        "max_sending_packets_len":
            max_sending_packets_len,

        "mean_sending_packets_len":
            mean_sending_packets_len,

        "median_sending_packets_len":
            median_sending_packets_len,

        "mode_sending_packets_len":
            mode_sending_packets_len,

        "dns_domain_name_length":
            domain_features[
                "dns_domain_name_length"
            ],

        "dns_subdomain_name_length":
            domain_features[
                "dns_subdomain_name_length"
            ],

        "dns_top_level_domain":
            domain_features[
                "dns_top_level_domain"
            ],

        "dns_second_level_domain":
            domain_features[
                "dns_second_level_domain"
            ],

        "character_entropy":
            domain_features[
                "character_entropy"
            ],

        "numerical_percentage":
            domain_features[
                "numerical_percentage"
            ],

        "max_continuous_alphabet_len":
            domain_features[
                "max_continuous_alphabet_len"
            ],

        "max_continuous_consonants_len":
            domain_features[
                "max_continuous_consonants_len"
            ],

        "vowels_consonant_ratio":
            domain_features[
                "vowels_consonant_ratio"
            ],

        "conv_freq_vowels_consonants":
            domain_features[
                "conv_freq_vowels_consonants"
            ]
    }

    return features


# ============================================================
# PREDICT FLOW
# ============================================================

def predict_flow(flow):

    features = extract_features(flow)

    if features is None:
        return None

    # Create a single-row DataFrame.
    # This preserves the feature names expected by
    # the trained sklearn pipeline.
    model_input = pd.DataFrame(
        [features],
        columns=LIVE_FEATURES
    )

    try:

        prediction = model.predict(
            model_input
        )[0]

        probabilities = model.predict_proba(
            model_input
        )[0]

        classes = list(
            model.classes_
        )

        if 1 in classes:

            phishing_index = classes.index(1)

            phishing_probability = float(
                probabilities[phishing_index]
            )

        else:

            phishing_probability = 0.0

        return {
            "prediction": int(prediction),

            "phishing_probability":
                phishing_probability,

            "features":
                features
        }

    except Exception as error:

        print(
            f"Prediction error: {error}",
            file=sys.stderr,
            flush=True
        )

        return None


# ============================================================
# CREATE FLOW RESULT
# ============================================================

def create_flow_result(flow_key, flow):

    prediction_result = predict_flow(
        flow
    )

    if prediction_result is None:

        return None

    result = {

        "type":
            "flow_result",

        "flowKey":
            str(flow_key),

        "srcIp":
            flow["src_ip"],

        "dstIp":
            flow["dst_ip"],

        "srcPort":
            flow["src_port"],

        "dstPort":
            flow["dst_port"],

        "protocol":
            flow["protocol"],

        "startTime":
            flow["start_time"],

        "endTime":
            flow["last_time"],

        "duration":
            flow["last_time"] -
            flow["start_time"],

        "prediction":
            prediction_result[
                "prediction"
            ],

        "phishingProbability":
            prediction_result[
                "phishing_probability"
            ],

        "features":
            prediction_result[
                "features"
            ]
    }

    return result


# ============================================================
# PROCESS ONE PACKET
# ============================================================

def process_packet(packet):

    timestamp = safe_float(
        packet.get("timestamp"),
        0.0
    )

    if timestamp <= 0:

        return

    # Ignore packets which don't have IP addresses.
    #
    # These can be ARP, Ethernet-only, etc.
    # They are not useful for our IP flow model.

    if (
        not packet.get("srcIp")
        or not packet.get("dstIp")
    ):

        return

    flow_key = create_flow_key(
        packet
    )

    if flow_key is None:

        return

    # --------------------------------------------------------
    # Check whether this is a new flow
    # --------------------------------------------------------

    if flow_key not in flows:

        flows[flow_key] = (
            create_flow(
                packet,
                timestamp
            )
        )

    # --------------------------------------------------------
    # Add packet
    # --------------------------------------------------------

    add_packet_to_flow(
        flows[flow_key],
        packet,
        timestamp
    )


# ============================================================
# EXPIRE OLD FLOWS
# ============================================================

def expire_flows(current_timestamp):

    expired_keys = []

    for flow_key, flow in list(
        flows.items()
    ):

        inactive_time = (
            current_timestamp -
            flow["last_time"]
        )

        if inactive_time >= FLOW_TIMEOUT:

            expired_keys.append(
                flow_key
            )

    # --------------------------------------------------------
    # Classify expired flows
    # --------------------------------------------------------

    for flow_key in expired_keys:

        flow = flows.pop(
            flow_key,
            None
        )

        if flow is None:
            continue

        result = create_flow_result(
            flow_key,
            flow
        )

        if result:

            print(
                json.dumps(
                    result,
                    separators=(",", ":")
                ),
                flush=True
            )


# ============================================================
# MAIN LOOP
# ============================================================

print(
    "Python packet processor started.",
    flush=True
)


for line in sys.stdin:

    try:

        line = line.strip()

        if not line:

            continue

        packet = json.loads(
            line
        )

        # ----------------------------------------------------
        # Process packet
        # ----------------------------------------------------

        process_packet(
            packet
        )

        # ----------------------------------------------------
        # Expire inactive flows
        # ----------------------------------------------------

        timestamp = safe_float(
            packet.get("timestamp"),
            0.0
        )

        if timestamp > 0:

            expire_flows(
                timestamp
            )

    except json.JSONDecodeError as error:

        print(
            f"Invalid JSON received: {error}",
            file=sys.stderr,
            flush=True
        )

    except Exception as error:

        print(
            f"Packet processing error: {error}",
            file=sys.stderr,
            flush=True
        )


# ============================================================
# PROCESS EXIT
# ============================================================

print(
    "Python packet processor stopped.",
    flush=True
)