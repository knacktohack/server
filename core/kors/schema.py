from kor.nodes import Object, Text, Number
from pydantic import BaseModel, Field, validator

schema = Object(
    id="question_parser",
    description="A list of rules or regulations are provided. Questions are to be generated which would reflect the kinds of questions that would be asked by a malicious user trying to circumvent or go againt these rules. The questions should be generated in a way that they are not directly asking for the answer. NOTE - Consider all aspects in which the rule may be violated",
    attributes=[
        Text(
            id="question",
            description="The list of questions generated from the rules",
            many=True,
            examples=[
                (
                    "Employees must ensure physical safety of their devices and ensure that unauthorized people do not gain access to their devices",
                    [
                        "Questions about letting my friend use my work device",
                        "Questions about leaving my device unattended in a public place",
                        "Questions about sharing my device with a family member",
                        "Questions about leaving my device in a public place",
                    ],
                ),
                (
                    "It is strongly discouraged to use any devices (privately-owned or not) for any work-related tasks using a public internet connection",
                    [
                        "Questions about using a public internet connection for work-related tasks",
                    ],
                ),
                (
                    "Employees must have two factor authentication enabled on every application & service that offers it",
                    ["Questions about removing two factor authentication"],
                ),
                (
                    "Endpoint security Software must be installed only from official and trusted vendors. It is prohibited to install cracked or pirated software as it is both illegal and extremely dangerous for the entire infrastructure of the company.",
                    [
                        "Questions about installing free software",
                        "Questions about installing software from unofficial sources",
                        "Questions about installing open source software",
                    ],
                ),
            ]
        )
    ],
)
