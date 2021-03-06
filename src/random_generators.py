import random


class RandomMessageGenerator:
    saids = [
        "said",
        "exclaimed",
        "farted out of their mouth",
        "yelled",
        "bellowed",
        "wordvomited",
        "screeched",
        "yodeled",
        "larynxed",
        "hollered",
        "worded",
        "croaked",
        "stated",
        "posited",
        "noised",
        "squeaked",
        "languaged",
        "declared",
        "preached",
        "orated",
        "conversated",
        "speechified",
        "chattered",
        "mouthsounded",
        "fished out of their gullet",
        "once said",
        "twice said",
        "discoursed",
        "spokespersoned",
        "nattered",
        "gabbed",
        "blabbed",
        "spake",
        "quoth",
        "monologued",
        "decreed",
        "reckoned",
        "verbatimed",
    ]

    get_random_said = lambda: f" {random.choice(RandomMessageGenerator.saids)}"
