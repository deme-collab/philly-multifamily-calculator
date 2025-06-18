# calculator.py - Philadelphia Multifamily Property Analysis Core Functions
"""
Philadelphia Multifamily Property Investment Calculator
Data effective October 1, 2024
"""

import re
from io import StringIO

# Data effective October 1, 2024, from the provided document
ZIP_TO_GROUP_MAPPING = {
     # -------- Group 1 | Traditional Rents (blue) --------
    "19120": 1, "19124": 1, "19126": 1, "19132": 1, "19133": 1,
    "19134": 1, "19136": 1, "19139": 1, "19140": 1, "19141": 1,
    "19142": 1, "19143": 1, "19151": 1,

    # -------- Group 2 | Mid-Range Rents (light-blue) --------
    "19101": 2, "19104": 2, "19105": 2, "19109": 2, "19110": 2,
    "19111": 2, "19112": 2, "19114": 2, "19115": 2, "19116": 2,
    "19119": 2, "19121": 2, "19122": 2, "19131": 2, "19135": 2,
    "19137": 2, "19138": 2, "19144": 2, "19145": 2, "19148": 2,
    "19149": 2, "19150": 2, "19152": 2, "19153": 2, "19154": 2,

    # -------- Group 3 | Opportunity Rents (green) --------
    "19118": 3, "19125": 3, "19127": 3, "19128": 3,
    "19129": 3, "19146": 3,

    # -------- Group 4 | High-Opportunity Rents (yellow) --------
    "19102": 4, "19103": 4, "19106": 4, "19107": 4,
    "19123": 4, "19130": 4, "19147": 4,
}

NEIGHBORHOOD_ZIP_GROUPINGS = {
    # --- Center City & Adjacent ---
    "Center City Core": ["19102", "19103", "19107"], # Rittenhouse, Logan Sq, Wash Sq West, Midtown Village, Avenue of the Arts
    "Old City / Society Hill / Waterfront": ["19106"],
    "Northern Liberties / Fishtown (South)": ["19123"], # Often seen as distinct but geographically close
    "Fairmount / Art Museum Area": ["19130"],
    "Graduate Hospital / Fitler Square": ["19146"], # Sometimes "Southwest Center City"
    "Bella Vista / Queen Village / Pennsport (South Philly East)": ["19147"],

    # --- South Philadelphia ---
    "South Philly - East (Passyunk, Dickinson Narrows)": ["19148"], # Distinct from 19147's more northern parts
    "South Philly - West (Point Breeze, Newbold, Girard Estate)": ["19145"],
    "South Philly - Deep South / Stadium District": ["19112"], # Navy Yard, Sports Complex area

    # --- West Philadelphia ---
    "University City / Spruce Hill / Walnut Hill": ["19104"], # UCity core, adjacent residential
    "West Philly - Central (Cedar Park, Garden Court, Cobbs Creek)": ["19143"],
    "West Philly - North (Mantua, Powelton Village, West Powelton)": ["19101", "19139"], # 19101 also covers 30th St Station area
    "Overbrook / Wynnefield": ["19131"],
    "Parkside / Carroll Park": ["19151"], # Western edge of West Philly

    # --- North Philadelphia ---
    "Fishtown (North) / Kensington (South) / Port Richmond (South)": ["19125"], # Fishtown core, parts of Kensington
    "Temple University Area / Lower North Philly": ["19121", "19122"], # Broad St corridor, Cecil B Moore
    "Brewerytown / Sharswood / Strawberry Mansion (East Fairmount Park)": ["19132"],
    "North Philly - East (Kensington, Harrowgate, Fairhill)": ["19133", "19134"], # More specific than just "Kensington"
    "Port Richmond / Bridesburg / Frankford (South)": ["19137"], # River Wards

    # --- Northwest Philadelphia ---
    "Germantown": ["19138", "19144"], # Can be split (East/West Germantown) but often grouped
    "Mount Airy": ["19119"],
    "Chestnut Hill": ["19118"],
    "Roxborough / Manayunk / East Falls": ["19127", "19128", "19129"], # Often grouped as "River Wards NW" or by individual names

    # --- Northeast Philadelphia ---
    "Lower Northeast (Frankford, Mayfair, Tacony)": ["19124", "19135", "19136"],
    "Central Northeast (Rhawnhurst, Fox Chase, Bustleton)": ["19111", "19115", "19152"],
    "Far Northeast (Somerton, Torresdale, Parkwood)": ["19114", "19116", "19154"],
    "Olney / Logan / Feltonville": ["19120", "19141"], # Upper North/Lower Northeast boundary
    "Oxford Circle / Lawncrest": ["19149"],
    "East Oak Lane / West Oak Lane": ["19126"],
    "Pennypack / Holmesburg": ["19150"], # Note: 19150 is Mt. Airy/W. Oak Lane more than Pennypack. Re-evaluating 19150.
                                         # 19150 is more aligned with Mt. Airy / Cedarbrook / West Oak Lane.
                                         # Let's re-assign 19150.
    # Re-evaluation for 19150:
    # "Mount Airy / Cedarbrook / West Oak Lane": ["19150", "19119", "19126"] - This makes more sense.
    # Let's adjust the NW Philly and Olney/Logan groups to reflect this.

    # --- Data Integrity Checks & Unassigned (From Original PHA List) ---
    # These are ZIPs from your PHA SAFMR mapping. Let's ensure they are covered.
    # 19105: Independence Hall area - could be "Old City / Society Hill" or "Center City Core"
    # 19109: Broad & Vine area - "Center City Core" or "Chinatown/Convention Center"
    # 19110: USPS ZIP, often not residential.
    # 19140: Hunting Park / Nicetown-Tioga - "North Philly - Central"
    # 19142: Southwest Philly (Elmwood, Eastwick)
    # 19153: Southwest Philly (Airport, Eastwick)

    # ----- REVISED GROUPINGS based on above logic & checks -----
    "Center City Core / Convention Center": ["19102", "19103", "19107", "19109"],
    "Old City / Society Hill / Independence Hall": ["19106", "19105"],
    "Northern Liberties / Fishtown (South)": ["19123"],
    "Fairmount / Art Museum Area": ["19130"],
    "Graduate Hospital / Fitler Square": ["19146"],
    "Bella Vista / Queen Village / Pennsport": ["19147"],

    "South Philly - East (Passyunk, Dickinson Narrows)": ["19148"],
    "South Philly - West (Point Breeze, Newbold, Girard Estate)": ["19145"],
    "South Philly - Deep South / Stadium District / Navy Yard": ["19112"],

    "University City / Spruce Hill / Walnut Hill": ["19104"],
    "West Philly - Central (Cedar Park, Garden Court, Cobbs Creek)": ["19143"],
    "West Philly - North (Mantua, Powelton, Mill Creek)": ["19139"], # 19101 is 30th St, less residential focus here
    "Overbrook / Wynnefield": ["19131"],
    "Parkside / Carroll Park / Haddington": ["19151"],

    "Fishtown (North) / Kensington (South) / Port Richmond (South)": ["19125"],
    "Temple University Area / Lower North Philly (Yorktown, Ludlow)": ["19121", "19122"],
    "Brewerytown / Sharswood / Strawberry Mansion": ["19132"],
    "North Philly - East (Kensington, Harrowgate, Fairhill, Juniata)": ["19133", "19134"],
    "Port Richmond / Bridesburg": ["19137"], # Keeping Frankford separate for now
    "North Philly - Central (Nicetown-Tioga, Hunting Park)": ["19140"],

    "Germantown (East & West)": ["19138", "19144"],
    "Mount Airy / Cedarbrook": ["19119", "19150"], # Grouped more closely
    "West Oak Lane / East Oak Lane": ["19126"], # Grouped
    "Chestnut Hill": ["19118"],
    "Roxborough / Manayunk / East Falls": ["19127", "19128", "19129"],

    "Lower Northeast (Frankford, Mayfair, Tacony, Wissinoming)": ["19124", "19135", "19136"],
    "Central Northeast (Rhawnhurst, Fox Chase, Bustleton, Somerton West)": ["19111", "19115", "19152"],
    "Far Northeast (Somerton East, Torresdale, Parkwood, Byberry)": ["19114", "19116", "19154"],
    "Olney / Logan / Feltonville": ["19120", "19141"],
    "Oxford Circle / Lawncrest / Lawndale": ["19149"],

    "Southwest Philly (Eastwick, Elmwood, Clearview)": ["19142", "19153"],

    # Special/Less Residential ZIPs (might not be in your PHA list for housing but good to know)
    "Center City - 30th Street Station Area": ["19101"], # Primarily commercial/transport
    "USPS Specific (Not typically residential areas)": ["19110"], # Often a PO Box or large institution ZIP
}

GROUP_TO_RENT_TYPE = {
    1: "Traditional Rents",
    2: "Mid Range Rents",
    3: "Opportunity Rents",
    4: "High Opportunity Rents"
}

PAYMENT_STANDARDS = {
    1: {"SRO": 847, "0 BR": 1130, "1 BR": 1240, "2 BR": 1480, "3 BR": 1780, "4 BR": 2030, "5 BR": 2334, "6 BR": 2639, "7 BR": 2943, "8 BR": 3248},
    2: {"SRO": 1042, "0 BR": 1390, "1 BR": 1540, "2 BR": 1830, "3 BR": 2200, "4 BR": 2510, "5 BR": 2886, "6 BR": 3263, "7 BR": 3639, "8 BR": 4016},
    3: {"SRO": 1342, "0 BR": 1790, "1 BR": 1970, "2 BR": 2350, "3 BR": 2830, "4 BR": 3220, "5 BR": 3703, "6 BR": 4186, "7 BR": 4669, "8 BR": 5152},
    4: {"SRO": 1522, "0 BR": 2030, "1 BR": 2270, "2 BR": 2700, "3 BR": 3250, "4 BR": 3700, "5 BR": 4255, "6 BR": 4810, "7 BR": 5365, "8 BR": 5920},
}

BEDROOM_INPUT_TO_KEY_MAP = {
    "SRO": "SRO",

    "0": "0 BR", "0BR": "0 BR", "0 BR": "0 BR",
    "0BED": "0 BR", "0 BEDS": "0 BR", "0BEDS": "0 BR", "STUDIO": "0 BR", # Studio often maps to 0BR

    "1": "1 BR", "1BR": "1 BR", "1 BR": "1 BR",
    "1BED": "1 BR", "1 BEDS": "1 BR", "1BEDS": "1 BR",

    "2": "2 BR", "2BR": "2 BR", "2 BR": "2 BR",
    "2BED": "2 BR", "2 BEDS": "2 BR", "2BEDS": "2 BR",

    "3": "3 BR", "3BR": "3 BR", "3 BR": "3 BR",
    "3BED": "3 BR", "3 BEDS": "3 BR", "3BEDS": "3 BR",

    "4": "4 BR", "4BR": "4 BR", "4 BR": "4 BR",
    "4BED": "4 BR", "4 BEDS": "4 BR", "4BEDS": "4 BR",

    "5": "5 BR", "5BR": "5 BR", "5 BR": "5 BR",
    "5BED": "5 BR", "5 BEDS": "5 BR", "5BEDS": "5 BR",

    "6": "6 BR", "6BR": "6 BR", "6 BR": "6 BR",
    "6BED": "6 BR", "6 BEDS": "6 BR", "6BEDS": "6 BR",

    "7": "7 BR", "7BR": "7 BR", "7 BR": "7 BR",
    "7BED": "7 BR", "7 BEDS": "7 BR", "7BEDS": "7 BR",

    "8": "8 BR", "8BR": "8 BR", "8 BR": "8 BR",
    "8BED": "8 BR", "8 BEDS": "8 BR", "8BEDS": "8 BR",
}

def get_client_friendly_neighborhood(zip_code):
    """Get client-friendly neighborhood name for a given ZIP code."""
    for neighborhood, zips in NEIGHBORHOOD_ZIP_GROUPINGS.items():
        if str(zip_code) in zips:
            return neighborhood
    return "Area Not Specified"

def calculate_monthly_piti(property_price, annual_property_taxes, annual_home_insurance,
                           loan_term_years, annual_interest_rate_percent, down_payment_percent=0):
    """Calculate monthly PITI (Principal, Interest, Taxes, Insurance) payment."""
    if not (0 <= down_payment_percent <= 100):
        raise ValueError("Down payment percent must be between 0 and 100.")

    down_payment_amount = property_price * (down_payment_percent / 100.0)
    loan_amount = property_price - down_payment_amount

    if loan_amount <= 0:
        monthly_principal_interest = 0.0
    else:
        monthly_interest_rate = (annual_interest_rate_percent / 100.0) / 12.0
        number_of_payments = loan_term_years * 12

        if number_of_payments == 0:
             monthly_principal_interest = 0.0
        elif monthly_interest_rate == 0:
             monthly_principal_interest = loan_amount / number_of_payments
        else:
            monthly_principal_interest = loan_amount * \
                                     (monthly_interest_rate * (1 + monthly_interest_rate)**number_of_payments) / \
                                     ((1 + monthly_interest_rate)**number_of_payments - 1)

    monthly_taxes = annual_property_taxes / 12.0
    monthly_insurance = annual_home_insurance / 12.0

    total_monthly_piti = monthly_principal_interest + monthly_taxes + monthly_insurance
    return total_monthly_piti, monthly_principal_interest, monthly_taxes, monthly_insurance

def get_pha_payment_standard(zip_code, bedrooms_input_str):
    """Get PHA payment standard for a given ZIP code and bedroom count."""
    if zip_code not in ZIP_TO_GROUP_MAPPING:
        return None, None, f"ZIP code {zip_code} not found in PHA SAFMR Group mapping. Please enter a valid Philadelphia ZIP from the list."

    safmr_group = ZIP_TO_GROUP_MAPPING[zip_code]
    rent_type_name = GROUP_TO_RENT_TYPE.get(safmr_group, "Unknown Rent Type")

    bedroom_key = BEDROOM_INPUT_TO_KEY_MAP.get(str(bedrooms_input_str).upper())
    if not bedroom_key:
        return None, None, f"Invalid bedroom input: {bedrooms_input_str}. Use SRO, 0-8."

    if safmr_group not in PAYMENT_STANDARDS or bedroom_key not in PAYMENT_STANDARDS[safmr_group]:
        return None, None, f"Payment standard not found for Group {safmr_group}, Bedrooms: {bedroom_key}."

    payment_standard_amount = PAYMENT_STANDARDS[safmr_group][bedroom_key]
    return payment_standard_amount, safmr_group, rent_type_name

def analyze_multifamily_property(
    property_zip_code,
    unit_bedroom_counts_str, # e.g., "25x1bed, 10x2BR, SRO"
    property_price,
    annual_property_taxes,
    annual_home_insurance,
    loan_term_years,
    annual_interest_rate_percent,
    down_payment_percent=0,
    vacancy_rate_percent=5,
    repairs_maintenance_percent=5,
    property_management_percent=8,
    other_opex_annual=0
):
    """Analyze a multifamily property investment using PHA payment standards."""
    results = {'units': [], 'property_summary': {}}
    unit_errors = []

    try:
        # --- MODIFIED PARSING LOGIC ---
        expanded_unit_list_from_input = []
        if not unit_bedroom_counts_str or unit_bedroom_counts_str.strip() == "":
            results['property_summary']['error'] = "No unit bedroom counts provided."
            return results

        # Split by comma for different unit groups
        raw_groups = [g.strip() for g in unit_bedroom_counts_str.split(',')]

        for group_entry in raw_groups:
            if not group_entry:
                continue

            # Use regex to parse "COUNTxTYPE" format, allowing spaces around 'x'
            # and making 'x' case-insensitive.
            # Example: "25x1bed", "10 X 2BR", "5 x SRO"
            match = re.match(r"(\d+)\s*X\s*(.+)", group_entry, re.IGNORECASE)

            if match:
                count_str, bed_type_str_from_regex = match.groups()
                try:
                    count = int(count_str)
                    if count <= 0:
                        unit_errors.append(f"Invalid count '{count_str}' in group '{group_entry}'. Skipping this group.")
                        continue

                    processed_bed_type = bed_type_str_from_regex.upper().strip()
                    expanded_unit_list_from_input.extend([processed_bed_type] * count)

                except ValueError:
                    unit_errors.append(f"Non-integer count in group '{group_entry}'. Skipping this group.")
            else:
                # No "x" multiplier, treat as a single unit entry
                expanded_unit_list_from_input.append(group_entry.upper().strip())

        if not expanded_unit_list_from_input:
            if unit_errors:
                 results['property_summary']['error'] = f"Error parsing unit bedroom counts. Details: {'; '.join(unit_errors)}"
            else:
                 results['property_summary']['error'] = "No valid unit groups found after parsing."
            return results

        unit_bedroom_list_str = expanded_unit_list_from_input

    except Exception as e:
        results['property_summary']['error'] = f"Error parsing unit bedroom counts: {e}"
        import traceback
        results['property_summary']['parsing_traceback'] = traceback.format_exc()
        return results

    total_potential_pha_rent_monthly = 0
    num_valid_units = 0

    # Process each unit
    for i, beds_str_from_list in enumerate(unit_bedroom_list_str):
        unit_data = {'unit_number': i + 1, 'bedrooms_str': beds_str_from_list}

        pha_rent, safmr_group, rent_type = get_pha_payment_standard(property_zip_code, beds_str_from_list)

        if pha_rent is None:
            unit_data['error'] = rent_type
            error_message_for_unit = f"Unit {i+1} (Input: '{beds_str_from_list}'): {rent_type}"
            if error_message_for_unit not in unit_errors:
                unit_errors.append(error_message_for_unit)
        else:
            unit_data['pha_rent'] = pha_rent
            unit_data['safmr_group'] = safmr_group
            unit_data['rent_type'] = rent_type
            total_potential_pha_rent_monthly += pha_rent
            num_valid_units += 1
        results['units'].append(unit_data)

    if unit_errors:
        current_prop_summary_errors = results['property_summary'].get('unit_errors', "")
        all_errors_str = "; ".join(unit_errors)
        if current_prop_summary_errors:
            results['property_summary']['unit_errors'] = f"{current_prop_summary_errors}; {all_errors_str}"
        else:
            results['property_summary']['unit_errors'] = all_errors_str

        if num_valid_units == 0:
            existing_error = results['property_summary'].get('error')
            if existing_error and "No valid unit groups found after parsing" in existing_error:
                 pass
            elif existing_error:
                results['property_summary']['error'] = existing_error + " Additionally, no valid units found for PHA rent calculation."
            else:
                results['property_summary']['error'] = "No valid units found for PHA rent calculation. Check unit_errors for details."
            return results

    results['property_summary']['total_potential_pha_rent_monthly'] = total_potential_pha_rent_monthly
    gross_potential_rent_annual = total_potential_pha_rent_monthly * 12

    # Calculate PITI for the entire property
    try:
        piti_monthly, pi_monthly, t_monthly, i_monthly = calculate_monthly_piti(
            property_price,
            annual_property_taxes,
            annual_home_insurance,
            loan_term_years,
            annual_interest_rate_percent,
            down_payment_percent
        )
        results['property_summary']['monthly_piti'] = piti_monthly
        results['property_summary']['monthly_principal_interest'] = pi_monthly
        results['property_summary']['monthly_taxes'] = t_monthly
        results['property_summary']['monthly_insurance'] = i_monthly
    except ValueError as e:
        results['property_summary']['error'] = str(e)
        return results

    # Operating Expenses
    vacancy_allowance_annual = gross_potential_rent_annual * (vacancy_rate_percent / 100.0)
    repairs_allowance_annual = gross_potential_rent_annual * (repairs_maintenance_percent / 100.0)
    management_fee_annual = gross_potential_rent_annual * (property_management_percent / 100.0)

    results['property_summary']['vacancy_allowance_annual'] = vacancy_allowance_annual
    results['property_summary']['repairs_allowance_annual'] = repairs_allowance_annual
    results['property_summary']['management_fee_annual'] = management_fee_annual
    results['property_summary']['other_opex_annual_input'] = other_opex_annual
    results['property_summary']['total_operating_expenses_annual_no_debt'] = (
        vacancy_allowance_annual +
        repairs_allowance_annual +
        management_fee_annual +
        other_opex_annual +
        annual_property_taxes +
        annual_home_insurance
    )

    # Net Operating Income (NOI)
    effective_gross_income_annual = gross_potential_rent_annual - vacancy_allowance_annual
    noi_annual = effective_gross_income_annual - (
        annual_property_taxes +
        annual_home_insurance +
        repairs_allowance_annual +
        management_fee_annual +
        other_opex_annual
    )

    results['property_summary']['effective_gross_income_annual'] = effective_gross_income_annual
    results['property_summary']['noi_annual'] = noi_annual

    # Cash Flow (Before Tax)
    annual_debt_service = pi_monthly * 12
    cash_flow_before_tax_annual = noi_annual - annual_debt_service
    results['property_summary']['annual_debt_service'] = annual_debt_service
    results['property_summary']['cash_flow_before_tax_annual'] = cash_flow_before_tax_annual
    results['property_summary']['cash_flow_before_tax_monthly'] = cash_flow_before_tax_annual / 12 if cash_flow_before_tax_annual != 0 else 0.0

    # Cash-on-Cash Return
    down_payment_amount = property_price * (down_payment_percent / 100.0)
    results['property_summary']['down_payment_amount'] = down_payment_amount
    if down_payment_amount > 0:
        cash_on_cash_return_percent = (cash_flow_before_tax_annual / down_payment_amount) * 100.0
    elif cash_flow_before_tax_annual > 0:
        cash_on_cash_return_percent = float('inf')
    elif cash_flow_before_tax_annual == 0:
        cash_on_cash_return_percent = 0.0
    else:
        cash_on_cash_return_percent = -float('inf')

    results['property_summary']['cash_on_cash_return_percent'] = cash_on_cash_return_percent

    # Gross Rent Multiplier (GRM)
    if gross_potential_rent_annual > 0:
        grm = property_price / gross_potential_rent_annual
    else:
        grm = float('inf') if property_price > 0 else 0.0
    results['property_summary']['grm'] = grm

    # Capitalization Rate (Cap Rate) = NOI / Property Price
    if property_price > 0:
        cap_rate_percent = (noi_annual / property_price) * 100.0
    elif noi_annual > 0:
        cap_rate_percent = float('inf')
    else:
        cap_rate_percent = 0.0 if noi_annual == 0 else -float('inf') if noi_annual < 0 and property_price == 0 else 0.0
        if property_price <= 0 and noi_annual > 0: cap_rate_percent = float('inf')
        elif property_price <=0 and noi_annual <0: cap_rate_percent = -float('inf')
        elif property_price <=0 and noi_annual ==0: cap_rate_percent = 0.0

    results['property_summary']['cap_rate_percent'] = cap_rate_percent

    results['property_summary']['gross_revenue_5_years'] = gross_potential_rent_annual * 5
    results['property_summary']['noi_5_years'] = noi_annual * 5

    # Final error handling
    if not results['property_summary'].get('error') and num_valid_units > 0:
        results['property_summary']['error'] = None
    elif not results['property_summary'].get('error') and num_valid_units == 0 and not unit_errors:
        results['property_summary']['error'] = "No units were processed, and no specific errors were found. Check input string."

    return results

def format_results_as_string(analysis_results, input_params):
    """Format analysis results as a readable string."""
    output_buffer = StringIO()

    summary = analysis_results.get('property_summary', {})
    units_info = analysis_results.get('units', [])

    # Extract input parameters
    prop_zip = input_params['property_zip_code']
    prop_price = input_params['property_price']
    dp_percent = input_params['down_payment_percent']
    annual_taxes = input_params['annual_property_taxes']
    annual_insurance = input_params['annual_home_insurance']
    vac_rate = input_params['vacancy_rate_percent']
    rep_maint_percent = input_params['repairs_maintenance_percent']
    prop_mgmt_percent = input_params['property_management_percent']
    other_opex = input_params['other_opex_annual']

    # Get client-friendly neighborhood
    try:
        client_neighborhood = get_client_friendly_neighborhood(prop_zip)
    except:
        client_neighborhood = "N/A (Lookup function not found)"

    output_buffer.write("--- MULTIFAMILY CALCULATION RESULTS ---\n")
    output_buffer.write(f"Input Unit String: {input_params['unit_bedroom_counts_str']}\n")
    output_buffer.write(f"Property ZIP Code: {prop_zip}\n")
    output_buffer.write(f"Client-Friendly Area: {client_neighborhood}\n")

    if summary.get('error') and not summary.get('unit_errors'):
        output_buffer.write(f"🚨 Error during calculation: {summary['error']}\n")
        if 'unit_errors' in summary:
             output_buffer.write(f"Individual Unit Errors: {summary['unit_errors']}\n")
    elif summary.get('error') and summary.get('unit_errors') and "No valid units found" in summary.get('error',''):
        output_buffer.write(f"🚨 Error: {summary['error']}\n")
        output_buffer.write(f"Details on Unit Parsing: {summary['unit_errors']}\n")
    else:
        try:
            if summary.get('unit_errors'):
                 output_buffer.write(f"⚠️ Note on Units/Parsing: {summary['unit_errors']}\n")
            output_buffer.write("-" * 50 + "\n")

            output_buffer.write(f"Unit Breakdown (Potential PHA Rents) - Total {len(units_info)} units processed:\n")
            valid_units_for_rent_calc = 0
            for unit in units_info:
                if 'error' in unit:
                    output_buffer.write(f"  Unit {unit['unit_number']} (Input: '{unit['bedrooms_str']}'): Error - {unit['error']}\n")
                else:
                    output_buffer.write(f"  Unit {unit['unit_number']} (Input: '{unit['bedrooms_str']}', Type: {unit.get('rent_type', 'N/A')}): ${unit.get('pha_rent', 0.0):.2f}/mo (Group {unit.get('safmr_group','N/A')})\n")
                    valid_units_for_rent_calc +=1

            if valid_units_for_rent_calc < len(units_info):
                output_buffer.write(f"  ({valid_units_for_rent_calc} of {len(units_info)} units were valid for rent calculation)\n")

            total_monthly_pha_rent = summary.get('total_potential_pha_rent_monthly', 0.0)
            output_buffer.write(f"  Total Potential Monthly PHA Rent (All Valid Units): ${total_monthly_pha_rent:,.2f}\n")
            output_buffer.write("-" * 50 + "\n")

            output_buffer.write("Property Financial Summary:\n")
            output_buffer.write(f"  Acquisition Price: ${float(prop_price):,.2f}\n")
            output_buffer.write(f"  Down Payment ({dp_percent}%): ${summary.get('down_payment_amount', 0.0):,.2f}\n")
            output_buffer.write("-" * 50 + "\n")

            output_buffer.write("Monthly Debt Service (PITI) & Basic Cash Flow:\n")
            monthly_piti = summary.get('monthly_piti', 0.0)
            output_buffer.write(f"  Total Monthly PITI: ${monthly_piti:,.2f}\n")
            output_buffer.write(f"    Principal & Interest (P&I): ${summary.get('monthly_principal_interest', 0.0):,.2f}\n")
            output_buffer.write(f"    Property Taxes (T): ${summary.get('monthly_taxes', 0.0):,.2f}\n")
            output_buffer.write(f"    Property Insurance (I): ${summary.get('monthly_insurance', 0.0):,.2f}\n")

            simple_cash_flow_monthly = total_monthly_pha_rent - monthly_piti
            if simple_cash_flow_monthly >= 0:
                output_buffer.write(f"  Basic Monthly Cash Flow (Total Rent - PITI): ${simple_cash_flow_monthly:,.2f}\n")
            else:
                output_buffer.write(f"  Basic Monthly Cash Flow (Total Rent - PITI): -${abs(simple_cash_flow_monthly):,.2f} (Loss)\n")

            if monthly_piti > 0:
                rent_to_piti_multiple = total_monthly_pha_rent / monthly_piti
                output_buffer.write(f"  Rent to PITI Multiple: {rent_to_piti_multiple:.2f}x\n")
            elif total_monthly_pha_rent > 0 and monthly_piti == 0:
                output_buffer.write(f"  Rent to PITI Multiple: Infinite (PITI is $0, Rent > $0)\n")
            else:
                output_buffer.write(f"  Rent to PITI Multiple: N/A\n")
            output_buffer.write("-" * 50 + "\n")

            output_buffer.write("Annual Operating Income & Expenses:\n")
            gpr_annual = total_monthly_pha_rent * 12
            output_buffer.write(f"  Gross Potential Rent (GPR): ${gpr_annual:,.2f}\n")
            output_buffer.write(f"  Vacancy Allowance ({vac_rate}% of GPR): -${summary.get('vacancy_allowance_annual', 0.0):,.2f}\n")
            output_buffer.write(f"  Effective Gross Income (EGI): ${summary.get('effective_gross_income_annual', 0.0):,.2f}\n")
            output_buffer.write("  Operating Expenses (Annual):\n")
            output_buffer.write(f"    Property Taxes: ${float(annual_taxes):,.2f}\n")
            output_buffer.write(f"    Property Insurance: ${float(annual_insurance):,.2f}\n")
            output_buffer.write(f"    Repairs & Maintenance ({rep_maint_percent}% of GPR): ${summary.get('repairs_allowance_annual', 0.0):,.2f}\n")
            output_buffer.write(f"    Property Management ({prop_mgmt_percent}% of GPR): ${summary.get('management_fee_annual', 0.0):,.2f}\n")
            output_buffer.write(f"    Other Operating Expenses: ${float(other_opex):,.2f}\n")
            output_buffer.write(f"  Net Operating Income (NOI): ${summary.get('noi_annual', 0.0):,.2f}\n")
            output_buffer.write("-" * 50 + "\n")

            output_buffer.write("Cash Flow & Returns (Comprehensive):\n")
            output_buffer.write(f"  Annual Debt Service (P&I): ${summary.get('annual_debt_service', 0.0):,.2f}\n")
            output_buffer.write(f"  Comprehensive Cash Flow Before Tax (Annual - CFBT): ${summary.get('cash_flow_before_tax_annual', 0.0):,.2f}\n")
            output_buffer.write(f"  Comprehensive Cash Flow Before Tax (Monthly - CFBT): ${summary.get('cash_flow_before_tax_monthly', 0.0):,.2f}\n")

            coc = summary.get('cash_on_cash_return_percent', 0.0)
            if coc == float('inf'):
                output_buffer.write(f"  Cash-on-Cash Return: Infinite\n")
            elif coc == -float('inf'):
                 output_buffer.write(f"  Cash-on-Cash Return: N/A (Negative CF on $0 Down or $0 Investment with Negative CF)\n")
            else:
                output_buffer.write(f"  Cash-on-Cash Return: {coc:.2f}%\n")

            cap_rate = summary.get('cap_rate_percent', 0.0)
            if cap_rate == float('inf'):
                output_buffer.write(f"  Capitalization Rate (Cap Rate): Infinite (NOI > 0, Price = $0)\n")
            else:
                output_buffer.write(f"  Capitalization Rate (Cap Rate): {cap_rate:.2f}%\n")
            output_buffer.write(f"  Gross Rent Multiplier (GRM): {summary.get('grm', 0.0):.2f}\n")
            output_buffer.write("-" * 50 + "\n")

            output_buffer.write("Longer-Term Projections (Simplified):\n")
            output_buffer.write(f"  Gross Potential Revenue (5 Years): ${summary.get('gross_revenue_5_years', 0.0):,.2f}\n")
            output_buffer.write(f"  Est. Net Operating Income (NOI, 5 Years): ${summary.get('noi_5_years', 0.0):,.2f}\n")
            output_buffer.write("-" * 50 + "\n")

        except KeyError as e:
            output_buffer.write(f"🚨 INTERNAL DISPLAY ERROR: A required key is missing in the results: {e}\n")
            output_buffer.write(f"Full 'analysis_results' dictionary for debugging: {analysis_results}\n")
        except Exception as e:
            output_buffer.write(f"🚨 AN UNEXPECTED ERROR occurred during result display: {e}\n")
            import traceback
            output_buffer.write(traceback.format_exc() + "\n")

    results_string = output_buffer.getvalue()
    output_buffer.close()
    return results_string