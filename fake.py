from re import split

from faker import Faker, providers

from schema import faker_config
from context import context

# export faker instance
fake: Faker


def init_faker() -> Faker:
    global fake

    # locale
    fake = Faker(faker_config.get("locales", None))

    # provider
    req_providers = faker_config.get("providers", [])
    for req in req_providers:
        if type(req) is str:
            provider = eval(f"providers.{req}", {"providers": providers})
            fake.add_provider(provider)
        else:
            name = req["name"]
            source = req["source"]
            with open(source) as f:
                content = f.read()
            elements = split(r"[,;\|\s]", content)
            custom_provider = providers.DynamicProvider(
                provider_name=name, elements=elements
            )
            fake.add_provider(custom_provider)

    # store into context
    context["fake"] = fake

    return fake
