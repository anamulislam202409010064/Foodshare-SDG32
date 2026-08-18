from datetime import datetime, date, timedelta
import json
import os

# ============================================================
# FoodShare: Food Donation Management System
# SDG 2: Zero Hunger
# GitHub-ready Python console application
# ============================================================

DATA_FILE = "foodshare_data.json"
DATE_FORMAT = "%d/%m/%Y"

donations = []
beneficiaries = []
distributions = []


# ----------------------------
# Data storage
# ----------------------------

def save_data():
    data = {
        "donations": donations,
        "beneficiaries": beneficiaries,
        "distributions": distributions
    }

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_data():
    global donations, beneficiaries, distributions

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            donations = data.get("donations", [])
            beneficiaries = data.get("beneficiaries", [])
            distributions = data.get("distributions", [])

        except (json.JSONDecodeError, OSError):
            print("Warning: Could not load saved data. Starting with empty records.")


# ----------------------------
# Utility functions
# ----------------------------

def generate_id(prefix, records, key):
    highest = 0

    for record in records:
        value = record.get(key, "")

        if value.startswith(prefix):
            try:
                number = int(value[1:])
                highest = max(highest, number)
            except ValueError:
                pass

    return f"{prefix}{highest + 1:03d}"


def get_positive_float(message):
    while True:
        try:
            value = float(input(message))

            if value <= 0:
                print("Value must be greater than 0.")
            else:
                return value

        except ValueError:
            print("Please enter a valid number.")


def get_positive_int(message):
    while True:
        try:
            value = int(input(message))

            if value <= 0:
                print("Value must be greater than 0.")
            else:
                return value

        except ValueError:
            print("Please enter a valid whole number.")


def get_valid_date(message):
    while True:
        user_date = input(message).strip()

        try:
            datetime.strptime(user_date, DATE_FORMAT)
            return user_date

        except ValueError:
            print("Invalid date. Use DD/MM/YYYY format.")


def parse_date(date_text):
    return datetime.strptime(date_text, DATE_FORMAT).date()


# ----------------------------
# Expiry and priority analysis
# ----------------------------

def check_expiry_status(expiry_date):
    expiry = parse_date(expiry_date)
    today = date.today()

    days_remaining = (expiry - today).days

    if days_remaining < 0:
        return "EXPIRED"
    elif days_remaining == 0:
        return "URGENT"
    elif days_remaining <= 3:
        return "EXPIRING SOON"
    else:
        return "SAFE"


def calculate_priority(expiry_date):
    status = check_expiry_status(expiry_date)

    if status == "EXPIRED":
        return "NOT AVAILABLE"
    elif status == "URGENT":
        return "PRIORITY 1"
    elif status == "EXPIRING SOON":
        return "PRIORITY 2"
    else:
        return "PRIORITY 3"


# ----------------------------
# Main menu
# ----------------------------

def display_main_menu():
    print("\n" + "=" * 66)
    print("          FOODSHARE DONATION MANAGEMENT SYSTEM")
    print("                 SDG 2: ZERO HUNGER")
    print("=" * 66)

    print("1.  Add Food Donation")
    print("2.  View All Donations")
    print("3.  Search Food")
    print("4.  Check Food Expiry Alerts")
    print("5.  View Donation Priority")
    print("6.  Register Beneficiary")
    print("7.  Distribute Food")
    print("8.  View Beneficiary Records")
    print("9.  View Statistics")
    print("10. SDG 2 Impact Dashboard")
    print("11. Load Demo Data")
    print("12. Reset All Data")
    print("13. Exit")

    print("=" * 66)


# ----------------------------
# Donation functions
# ----------------------------

def add_food_donation():
    print("\n--- Add Food Donation ---")

    donation_id = generate_id("D", donations, "donation_id")

    donor_name = input("Donor name: ").strip()
    food_name = input("Food name: ").strip()
    category = input("Food category: ").strip()

    quantity = get_positive_float("Quantity: ")
    unit = input("Unit (kg / packs / boxes / cans): ").strip()

    donation_date = get_valid_date("Donation date (DD/MM/YYYY): ")
    expiry_date = get_valid_date("Expiry date (DD/MM/YYYY): ")

    donation = {
        "donation_id": donation_id,
        "donor_name": donor_name,
        "food_name": food_name,
        "category": category,
        "quantity": quantity,
        "original_quantity": quantity,
        "unit": unit,
        "donation_date": donation_date,
        "expiry_date": expiry_date
    }

    donations.append(donation)
    save_data()

    print("\nDonation successfully recorded.")
    print("Donation ID :", donation_id)
    print("Status      :", check_expiry_status(expiry_date))
    print("Priority    :", calculate_priority(expiry_date))


def view_all_donations():
    print("\n--- All Food Donations ---")

    if not donations:
        print("No donation records found.")
        return

    print(
        f"{'ID':<7}"
        f"{'Food':<18}"
        f"{'Available':<14}"
        f"{'Unit':<10}"
        f"{'Expiry':<14}"
        f"{'Status':<18}"
        f"{'Priority':<15}"
    )

    print("-" * 96)

    for donation in donations:
        print(
            f"{donation['donation_id']:<7}"
            f"{donation['food_name'][:16]:<18}"
            f"{donation['quantity']:<14.2f}"
            f"{donation['unit']:<10}"
            f"{donation['expiry_date']:<14}"
            f"{check_expiry_status(donation['expiry_date']):<18}"
            f"{calculate_priority(donation['expiry_date']):<15}"
        )


def search_food():
    print("\n--- Search Food ---")

    if not donations:
        print("No donation records found.")
        return

    keyword = input("Enter food name or category: ").strip().lower()
    found = False

    for donation in donations:
        if (
            keyword in donation["food_name"].lower()
            or keyword in donation["category"].lower()
            or keyword in donation["donor_name"].lower()
        ):
            found = True

            print("\nDonation ID :", donation["donation_id"])
            print("Donor       :", donation["donor_name"])
            print("Food        :", donation["food_name"])
            print("Category    :", donation["category"])
            print(
                "Available   :",
                donation["quantity"],
                donation["unit"]
            )
            print("Expiry Date :", donation["expiry_date"])
            print("Status      :", check_expiry_status(donation["expiry_date"]))
            print("Priority    :", calculate_priority(donation["expiry_date"]))

    if not found:
        print("No matching food found.")


def check_food_expiry_alerts():
    print("\n--- Food Expiry Alerts ---")

    if not donations:
        print("No donation records found.")
        return

    alerts = 0

    for donation in donations:
        status = check_expiry_status(donation["expiry_date"])

        if status != "SAFE" and donation["quantity"] > 0:
            alerts += 1

            print(
                donation["donation_id"],
                "-",
                donation["food_name"],
                "-",
                status,
                "-",
                donation["quantity"],
                donation["unit"]
            )

    if alerts == 0:
        print("No food requires immediate attention.")


def view_donation_priority():
    print("\n--- Donation Distribution Priority ---")

    if not donations:
        print("No donation records found.")
        return

    priority_rank = {
        "PRIORITY 1": 1,
        "PRIORITY 2": 2,
        "PRIORITY 3": 3,
        "NOT AVAILABLE": 4
    }

    sorted_donations = sorted(
        donations,
        key=lambda item: (
            priority_rank[calculate_priority(item["expiry_date"])],
            parse_date(item["expiry_date"])
        )
    )

    for number, donation in enumerate(sorted_donations, start=1):
        print(
            f"{number}. "
            f"{donation['food_name']} - "
            f"{calculate_priority(donation['expiry_date'])} - "
            f"{check_expiry_status(donation['expiry_date'])}"
        )


# ----------------------------
# Beneficiary functions
# ----------------------------

def register_beneficiary():
    print("\n--- Register Beneficiary ---")

    beneficiary_id = generate_id(
        "B",
        beneficiaries,
        "beneficiary_id"
    )

    name = input("Beneficiary / organisation name: ").strip()
    beneficiary_type = input(
        "Type (Household / NGO / Community Centre): "
    ).strip()

    people_supported = get_positive_int(
        "Number of people supported: "
    )

    contact_number = input("Contact number: ").strip()

    beneficiary = {
        "beneficiary_id": beneficiary_id,
        "name": name,
        "type": beneficiary_type,
        "people_supported": people_supported,
        "contact_number": contact_number
    }

    beneficiaries.append(beneficiary)
    save_data()

    print("\nBeneficiary successfully registered.")
    print("Beneficiary ID:", beneficiary_id)


def find_donation(donation_id):
    for donation in donations:
        if donation["donation_id"].lower() == donation_id.lower():
            return donation

    return None


def find_beneficiary(beneficiary_id):
    for beneficiary in beneficiaries:
        if beneficiary["beneficiary_id"].lower() == beneficiary_id.lower():
            return beneficiary

    return None


# ----------------------------
# Distribution functions
# ----------------------------

def distribute_food():
    print("\n--- Distribute Food ---")

    if not donations:
        print("No food donations available.")
        return

    if not beneficiaries:
        print("No beneficiaries registered.")
        return

    donation_id = input("Donation ID: ").strip()
    donation = find_donation(donation_id)

    if donation is None:
        print("Donation ID not found.")
        return

    if check_expiry_status(donation["expiry_date"]) == "EXPIRED":
        print("Expired food cannot be distributed.")
        return

    if donation["quantity"] <= 0:
        print("This donation has no remaining stock.")
        return

    beneficiary_id = input("Beneficiary ID: ").strip()
    beneficiary = find_beneficiary(beneficiary_id)

    if beneficiary is None:
        print("Beneficiary ID not found.")
        return

    print(
        "Available stock:",
        donation["quantity"],
        donation["unit"]
    )

    quantity = get_positive_float(
        "Quantity to distribute: "
    )

    if quantity > donation["quantity"]:
        print("Insufficient stock.")
        return

    distribution_id = generate_id(
        "T",
        distributions,
        "distribution_id"
    )

    donation["quantity"] -= quantity

    distribution = {
        "distribution_id": distribution_id,
        "beneficiary_id": beneficiary_id,
        "beneficiary_name": beneficiary["name"],
        "donation_id": donation_id,
        "food_name": donation["food_name"],
        "quantity": quantity,
        "unit": donation["unit"],
        "distribution_date": date.today().strftime(DATE_FORMAT)
    }

    distributions.append(distribution)
    save_data()

    print("\nDistribution successful.")
    print("Transaction ID :", distribution_id)
    print(
        "Remaining stock:",
        donation["quantity"],
        donation["unit"]
    )


def view_beneficiary_records():
    print("\n--- Beneficiary Records ---")

    if not beneficiaries:
        print("No beneficiary records found.")
        return

    print(
        f"{'ID':<7}"
        f"{'Name':<28}"
        f"{'Type':<22}"
        f"{'People':<10}"
    )

    print("-" * 70)

    for beneficiary in beneficiaries:
        print(
            f"{beneficiary['beneficiary_id']:<7}"
            f"{beneficiary['name'][:26]:<28}"
            f"{beneficiary['type'][:20]:<22}"
            f"{beneficiary['people_supported']:<10}"
        )

    print("\nDistribution History")
    print("-" * 70)

    if not distributions:
        print("No distribution records found.")
        return

    for record in distributions:
        print(
            f"{record['distribution_id']} | "
            f"{record['beneficiary_name']} | "
            f"{record['food_name']} | "
            f"{record['quantity']} {record['unit']} | "
            f"{record['distribution_date']}"
        )


# ----------------------------
# Statistics
# ----------------------------

def calculate_total_received():
    return sum(
        donation["original_quantity"]
        for donation in donations
    )


def calculate_total_remaining():
    return sum(
        donation["quantity"]
        for donation in donations
    )


def calculate_total_distributed():
    return sum(
        record["quantity"]
        for record in distributions
    )


def view_statistics():
    print("\n--- Food Donation Statistics ---")

    total_received = calculate_total_received()
    total_remaining = calculate_total_remaining()
    total_distributed = calculate_total_distributed()

    total_people = sum(
        beneficiary["people_supported"]
        for beneficiary in beneficiaries
    )

    expired_food = sum(
        donation["quantity"]
        for donation in donations
        if check_expiry_status(donation["expiry_date"]) == "EXPIRED"
    )

    distribution_rate = (
        total_distributed / total_received * 100
        if total_received > 0
        else 0
    )

    print("Total Donation Records       :", len(donations))
    print("Total Food Received          :", round(total_received, 2))
    print("Food Distributed             :", round(total_distributed, 2))
    print("Remaining Food               :", round(total_remaining, 2))
    print("Expired Remaining Food       :", round(expired_food, 2))
    print("Registered Beneficiaries     :", len(beneficiaries))
    print("People Supported             :", total_people)
    print(
        "Successful Distribution Rate :",
        f"{distribution_rate:.2f}%"
    )


# ----------------------------
# SDG dashboard
# ----------------------------

def sdg_impact_dashboard():
    print("\n" + "=" * 66)
    print("             FOODSHARE SDG 2 IMPACT DASHBOARD")
    print("=" * 66)

    total_received = calculate_total_received()
    total_remaining = calculate_total_remaining()
    total_distributed = calculate_total_distributed()

    total_people = sum(
        beneficiary["people_supported"]
        for beneficiary in beneficiaries
    )

    rate = (
        total_distributed / total_received * 100
        if total_received > 0
        else 0
    )

    print("Total Donations          :", len(donations))
    print("Food Received            :", round(total_received, 2))
    print("Food Distributed         :", round(total_distributed, 2))
    print("Remaining Stock          :", round(total_remaining, 2))
    print("Beneficiaries Registered :", len(beneficiaries))
    print("People Supported         :", total_people)
    print("Distribution Rate        :", f"{rate:.2f}%")

    print("\nFood Requiring Attention")
    print("-" * 66)

    urgent_found = False

    for donation in donations:
        status = check_expiry_status(donation["expiry_date"])

        if (
            status in ("URGENT", "EXPIRING SOON")
            and donation["quantity"] > 0
        ):
            urgent_found = True

            print(
                f"{donation['food_name']} - "
                f"{donation['quantity']} {donation['unit']} - "
                f"{status}"
            )

    if not urgent_found:
        print("No urgent or soon-to-expire food items.")

    print("\nSDG 2 Contribution")
    print("-" * 66)

    print(
        f"{round(total_distributed, 2)} total units of donated food "
        "have been distributed."
    )

    print(
        "FoodShare helps organisations monitor donations, "
        "prioritise food close to expiry and distribute food "
        "to communities in need."
    )

    print("=" * 66)


# ----------------------------
# Demo / reset functions
# ----------------------------

def load_demo_data():
    donations.clear()
    beneficiaries.clear()
    distributions.clear()

    today = date.today()

    demo_donations = [
        {
            "donation_id": "D001",
            "donor_name": "FreshMart",
            "food_name": "Rice",
            "category": "Dry Food",
            "quantity": 50.0,
            "original_quantity": 50.0,
            "unit": "kg",
            "donation_date": today.strftime(DATE_FORMAT),
            "expiry_date": (
                today + timedelta(days=30)
            ).strftime(DATE_FORMAT)
        },
        {
            "donation_id": "D002",
            "donor_name": "Daily Bakery",
            "food_name": "Bread",
            "category": "Bakery",
            "quantity": 20.0,
            "original_quantity": 20.0,
            "unit": "packs",
            "donation_date": today.strftime(DATE_FORMAT),
            "expiry_date": (
                today + timedelta(days=2)
            ).strftime(DATE_FORMAT)
        },
        {
            "donation_id": "D003",
            "donor_name": "Care Grocer",
            "food_name": "Milk",
            "category": "Dairy",
            "quantity": 15.0,
            "original_quantity": 15.0,
            "unit": "boxes",
            "donation_date": today.strftime(DATE_FORMAT),
            "expiry_date": today.strftime(DATE_FORMAT)
        },
        {
            "donation_id": "D004",
            "donor_name": "Green Farm",
            "food_name": "Vegetables",
            "category": "Fresh Produce",
            "quantity": 18.0,
            "original_quantity": 18.0,
            "unit": "kg",
            "donation_date": today.strftime(DATE_FORMAT),
            "expiry_date": (
                today + timedelta(days=3)
            ).strftime(DATE_FORMAT)
        }
    ]

    demo_beneficiaries = [
        {
            "beneficiary_id": "B001",
            "name": "Hope Community Centre",
            "type": "Community Centre",
            "people_supported": 25,
            "contact_number": "0123456789"
        },
        {
            "beneficiary_id": "B002",
            "name": "Care Shelter",
            "type": "NGO",
            "people_supported": 18,
            "contact_number": "0198765432"
        }
    ]

    donations.extend(demo_donations)
    beneficiaries.extend(demo_beneficiaries)

    save_data()

    print("\nDemo data loaded successfully.")
    print("Try options 2, 4, 5, 7, 9 and 10.")


def reset_all_data():
    confirmation = input(
        "Type RESET to delete all saved records: "
    ).strip()

    if confirmation == "RESET":
        donations.clear()
        beneficiaries.clear()
        distributions.clear()

        save_data()

        print("All records have been deleted.")
    else:
        print("Reset cancelled.")


# ----------------------------
# Main program
# ----------------------------

def main():
    load_data()

    while True:
        display_main_menu()

        choice = input(
            "Enter your choice (1-13): "
        ).strip()

        if choice == "1":
            add_food_donation()

        elif choice == "2":
            view_all_donations()

        elif choice == "3":
            search_food()

        elif choice == "4":
            check_food_expiry_alerts()

        elif choice == "5":
            view_donation_priority()

        elif choice == "6":
            register_beneficiary()

        elif choice == "7":
            distribute_food()

        elif choice == "8":
            view_beneficiary_records()

        elif choice == "9":
            view_statistics()

        elif choice == "10":
            sdg_impact_dashboard()

        elif choice == "11":
            load_demo_data()

        elif choice == "12":
            reset_all_data()

        elif choice == "13":
            print("\nThank you for using FoodShare.")
            print("Together we support SDG 2: Zero Hunger.")
            break

        else:
            print(
                "Invalid choice. Please select a number from 1 to 13."
            )


if __name__ == "__main__":
    main()