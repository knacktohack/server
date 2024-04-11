from kor.nodes import Object, Text, Number
from pydantic import BaseModel, Field, validator

listElement = Object(
    id="listElement",
    description="The question and its priority",
    attributes=[
        Text(
            id="question",
            description="A question generated from the rules",
        ),
        Number(
            id="priority",
            description="The priority of the question from 1 to 10. A question with a higher priority is more likely to be asked by a malicious employee",
        ),
    ],
)
schema = Object(
    id="question_parser",
    description="""A paragraph of rules or regulations are provided.
    Find the rules in the paragraph pertaining to employee conduct and security.
    Questions are to be generated which would reflect the kinds of questions that would be asked by a malicious employee trying to circumvent or go againt any of these rules.
    The questions should be generated in an indirect way. NOTE - Consider all aspects in which the rule may be violated.
    Generate a maximum of 3 most relevant questions""",
    attributes=[listElement],
    examples=[
        (
            "Employees must ensure physical safety of their devices and ensure that unauthorized people do not gain access to their devices",
            {
                "listElement": [
                    {
                        "question": "Questions about leaving my device in a public place",
                        "priority": 6,
                    },
                    {
                        "question": "Questions about letting my friend use my work device",
                        "priority": 9,
                    },
                ]
            },
        ),
        (
            "It is strongly discouraged to use any devices (privately-owned or not) for any work-related tasks using a public internet connection",
            {
                "listElement": [
                    {
                        "question": "Questions about using a public internet connection for work-related tasks",
                        "priority": 6,
                    }
                ]
            },
        ),
        (
            "Employees must have two factor authentication enabled on every application & service that offers it",
            {
                "listElement": [
                    {
                        "question": "Questions about not using two factor authentication",
                        "priority": 7,
                    }
                ]
            },
        ),
        (
            "Endpoint security Software must be installed only from official and trusted vendors. It is prohibited to install cracked or pirated software as it is both illegal and extremely dangerous for the entire infrastructure of the company.",
            {
                "listElement": [
                    {
                        "question": "Questions about installing cracked software",
                        "priority": 10,
                    },
                    {
                        "question": "Questions about installing free software",
                        "priority": 7,
                    },
                    {
                        "question": "Questions about installing open source software",
                        "priority": 5,
                    },
                ]
            },
        ),
        (
            "laptop is banned",
            {
                "listElement": [
                    {"question": "Questions about using a laptop", "priority": 5}
                ]
            },
        ),
    ],
    many=True,
)
