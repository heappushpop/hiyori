from os import environ


def domain_name(request):
    return {"domain_name": environ["DOMAIN_NAME"]}
