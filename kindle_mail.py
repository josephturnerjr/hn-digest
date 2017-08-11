import requests

FROM_EMAIL = "Joseph - Photobooth Creator Support <kindle@gymkeeper.thejosephturner.com>"

DOMAIN = "gymkeeper.thejosephturner.com"

def send_email(api_key, to_addr, fd):
    r = requests.post(
        "https://api.mailgun.net/v2/%s/messages" % DOMAIN,
        auth=("api", api_key),
        files={'attachment':  ("hn.html", fd)},
        data={"from": FROM_EMAIL,
              "to": [to_addr],
              "text": "yo",
              "subject": "yo"})
    print(r.status_code)
    print(r.text)
    return r
