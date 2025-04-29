from typing import Optional

SHOWROOM_INFO = {
    "locations": [
        {
            "name": "S. Salvatore di Cogorno (GE)",
            "address": "Corso Matteotti, 4",
            "phone": "+39 340 36 17 157",
            "hours": {
                "Monday": "Closed",
                "Tuesday–Saturday": "9:30–13:00 / 15:30–19:30",
                "Sunday": "15:30–19:30"
            }
        },
        {
            "name": "Sestri Levante (GE)",
            "address": "Via Fascie, 20",
            "phone": "+39 339 19 35 185",
            "hours": {
                "Monday–Saturday": "9:30–13:00 / 15:30–19:30",
                "Sunday": "09:30–13:00 / 15:30–19:30"
            }
        }
    ],
    "emails": [
        "info@bixiodesign.com",
        "progetti@bixiodesign.com"
    ],
    "products": [
        "kitchens", "tables and chairs", "bathrooms", "libraries/bookshelves", "beds"
    ],
    "material": "All products are made from teak wood.",
    "website": "https://www.bixiodesign.com/"
}

def get_showroom_response(query: str, language: Optional[str] = "en") -> str:
    query = query.lower()

    if "where" in query or "location" in query or "address" in query:
        locations = "\n\n".join([
            f"{loc['name']}\nAddress: {loc['address']}\nPhone: {loc['phone']}"
            for loc in SHOWROOM_INFO["locations"]
        ])
        return f"Our showrooms are located at:\n\n{locations}"

    elif "open" in query or "hours" in query or "time" in query:
        hours = "\n\n".join([
            f"{loc['name']} Hours:\n" + "\n".join(f"{day}: {time}" for day, time in loc["hours"].items())
            for loc in SHOWROOM_INFO["locations"]
        ])
        return f"Our opening hours are:\n\n{hours}"

    elif "contact" in query or "phone" in query or "email" in query:
        phones = "\n".join([f"{loc['name']}: {loc['phone']}" for loc in SHOWROOM_INFO["locations"]])
        emails = ", ".join(SHOWROOM_INFO["emails"])
        return f"📞 Phones:\n{phones}\n\n✉️ Emails: {emails}"

    elif "deliver" in query or "ship" in query:
        return "✅ Yes, we offer delivery to various cities including Milan and surrounding regions."

    elif "products" in query or "sell" in query or "offer" in query:
        product_list = ", ".join(SHOWROOM_INFO["products"])
        return f"We offer: {product_list}.\nAll made from premium teak wood."

    elif "website" in query:
        return f"Our official website is: {SHOWROOM_INFO['website']}"

    elif "contact" in query or "phone" in query or "email" in query or "reach" in query:
        contacts = []
        for loc in SHOWROOM_INFO["locations"]:
            contact_block = (
                f"{loc['name']}:\n"
                f"Address: {loc['address']}\n"
                f"Phone: {loc['phone']}"
            )
            contacts.append(contact_block)
        emails = ", ".join(SHOWROOM_INFO["emails"])
        contacts.append(f"Emails: {emails}")
        contacts.append(f"Website: {SHOWROOM_INFO['website']}")
        return "\n\n".join(contacts)


    else:
        # Fallback info
        fallback = "\n".join([
            f"{loc['name']}: {loc['address']} | {loc['phone']}"
            for loc in SHOWROOM_INFO["locations"]
        ])
        return f"I'm here to help with showroom information. Here's a quick overview:\n\n{fallback}"
